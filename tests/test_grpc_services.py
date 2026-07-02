"""
gRPC Integration Tests for BimaGrid Services.

Tests the full USSD ↔ Backend gRPC channel by spinning up a real in-process
gRPC server using the generated bimagrid_pb2_grpc stubs, then exercising
each RPC method with real client stubs.
"""
from __future__ import annotations

import os
import sys
import threading
from concurrent import futures

import grpc
import pytest

# ─── Load generated stubs (flat copy in tests/grpc_stubs/) ───────────────────
STUBS_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "grpc_stubs"))
sys.path.insert(0, STUBS_PATH)

import bimagrid_pb2
import bimagrid_pb2_grpc


# ─── In-Process Test Servicers ───────────────────────────────────────────────

class _OracleServicer(bimagrid_pb2_grpc.OracleServiceServicer):
    """Oracle gRPC service: accepts signed parametric data from Rust nodes."""
    def __init__(self):
        self.received: list[bimagrid_pb2.OracleDataRequest] = []

    def SubmitData(self, request, context):
        self.received.append(request)
        return bimagrid_pb2.OracleDataResponse(
            success=True,
            message="Oracle data received and verified via gRPC."
        )


class _UssdServicer(bimagrid_pb2_grpc.UssdServiceServicer):
    """USSD gRPC service: handles farmer interactions proxied from the USSD gateway."""
    def RegisterFarmer(self, request, context):
        if not request.phone or not request.ward_code:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("phone and ward_code are required")
            return bimagrid_pb2.RegisterFarmerResponse()
        return bimagrid_pb2.RegisterFarmerResponse(
            success=True,
            message="Farmer registered successfully.",
            policy_number=f"POL-{request.ward_code}-TEST"
        )

    def GetPolicyStatus(self, request, context):
        if request.phone == "254700000000":
            return bimagrid_pb2.PolicyStatusResponse(
                success=True, status="ACTIVE",
                message="Policy is active.",
                next_payment_date="2027-01-01"
            )
        return bimagrid_pb2.PolicyStatusResponse(
            success=False, status="NOT_FOUND",
            message="No policy for this number.",
            next_payment_date=""
        )

    def FileClaim(self, request, context):
        if request.loss_type not in ("drought", "flood", "hail", "frost"):
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details(f"Unknown loss_type: {request.loss_type}")
            return bimagrid_pb2.FileClaimResponse()
        return bimagrid_pb2.FileClaimResponse(
            success=True,
            message="Parametric claim auto-evaluated.",
            claim_reference=f"CLM-{request.phone[-4:]}-{request.loss_type.upper()}"
        )


# ─── Pytest Fixtures ─────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def grpc_server():
    """Spin up a real in-process gRPC server for the duration of the module."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    oracle_servicer = _OracleServicer()
    ussd_servicer = _UssdServicer()

    bimagrid_pb2_grpc.add_OracleServiceServicer_to_server(oracle_servicer, server)
    bimagrid_pb2_grpc.add_UssdServiceServicer_to_server(ussd_servicer, server)

    port = server.add_insecure_port("[::]:50052")  # Use 50052 to avoid collision
    server.start()

    yield server, oracle_servicer, ussd_servicer, port

    server.stop(grace=0)


@pytest.fixture(scope="module")
def oracle_stub(grpc_server):
    server, *_ = grpc_server
    channel = grpc.insecure_channel("localhost:50052")
    return bimagrid_pb2_grpc.OracleServiceStub(channel)


@pytest.fixture(scope="module")
def ussd_stub(grpc_server):
    server, *_ = grpc_server
    channel = grpc.insecure_channel("localhost:50052")
    return bimagrid_pb2_grpc.UssdServiceStub(channel)


# ─── Oracle gRPC Tests ────────────────────────────────────────────────────────

class TestOracleGrpc:
    def test_submit_data_success(self, oracle_stub, grpc_server):
        *_, oracle_servicer, __, ___ = grpc_server
        _, oracle_svc, *__ = grpc_server

        req = bimagrid_pb2.OracleDataRequest(
            oracle_id="oracle-1",
            h3_index="8928308280fffff",
            timestamp="2026-07-02T06:00:00Z",
            rainfall_mm=15.5,
            ndvi=0.62,
            soil_moisture=0.31,
            data_sources=["open-meteo", "nasa-power"],
            signature="0xdeadbeef1234"
        )
        resp = oracle_stub.SubmitData(req)
        assert resp.success is True
        assert "verified" in resp.message.lower()

    def test_submit_data_stored_by_servicer(self, oracle_stub, grpc_server):
        _, oracle_svc, *__ = grpc_server
        before = len(oracle_svc.received)

        oracle_stub.SubmitData(bimagrid_pb2.OracleDataRequest(
            oracle_id="oracle-2",
            h3_index="8928308280ffffe",
            timestamp="2026-07-02T07:00:00Z",
            rainfall_mm=8.0,
            ndvi=0.35,
            soil_moisture=0.14,
            data_sources=["chirps"],
            signature="0xabcdef5678"
        ))
        assert len(oracle_svc.received) == before + 1

    def test_submit_data_multiple_oracles(self, oracle_stub):
        responses = []
        for i, (rainfall, sig) in enumerate([
            (12.0, "0xsig001"), (18.5, "0xsig002"), (14.2, "0xsig003")
        ]):
            resp = oracle_stub.SubmitData(bimagrid_pb2.OracleDataRequest(
                oracle_id=f"oracle-{i+1}",
                h3_index="8928308280fffff",
                timestamp="2026-07-02T23:00:00Z",
                rainfall_mm=rainfall,
                ndvi=0.5,
                soil_moisture=0.25,
                data_sources=["open-meteo"],
                signature=sig
            ))
            responses.append(resp)
        assert all(r.success for r in responses)


# ─── USSD gRPC Tests ─────────────────────────────────────────────────────────

class TestUssdGrpc:
    def test_register_farmer_success(self, ussd_stub):
        resp = ussd_stub.RegisterFarmer(bimagrid_pb2.RegisterFarmerRequest(
            phone="254711111111",
            ward_code="WARD-KISUMU-01",
            crop="MAIZE",
            acreage="2.5",
            mpesa_number="254711111111"
        ))
        assert resp.success is True
        assert "WARD-KISUMU-01" in resp.policy_number
        assert resp.message != ""

    def test_register_farmer_missing_fields_returns_error(self, ussd_stub):
        with pytest.raises(grpc.RpcError) as exc_info:
            ussd_stub.RegisterFarmer(bimagrid_pb2.RegisterFarmerRequest(
                phone="",
                ward_code="",
                crop="BEANS",
                acreage="1",
                mpesa_number=""
            ))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    def test_get_policy_status_active(self, ussd_stub):
        resp = ussd_stub.GetPolicyStatus(bimagrid_pb2.PolicyStatusRequest(
            phone="254700000000"
        ))
        assert resp.success is True
        assert resp.status == "ACTIVE"
        assert resp.next_payment_date == "2027-01-01"

    def test_get_policy_status_not_found(self, ussd_stub):
        resp = ussd_stub.GetPolicyStatus(bimagrid_pb2.PolicyStatusRequest(
            phone="254799999999"
        ))
        assert resp.success is False
        assert resp.status == "NOT_FOUND"

    @pytest.mark.parametrize("loss_type", ["drought", "flood", "hail", "frost"])
    def test_file_claim_all_peril_types(self, ussd_stub, loss_type):
        resp = ussd_stub.FileClaim(bimagrid_pb2.FileClaimRequest(
            phone="254711222333",
            loss_type=loss_type,
            description=f"Test {loss_type} claim"
        ))
        assert resp.success is True
        assert loss_type.upper() in resp.claim_reference

    def test_file_claim_invalid_loss_type(self, ussd_stub):
        with pytest.raises(grpc.RpcError) as exc_info:
            ussd_stub.FileClaim(bimagrid_pb2.FileClaimRequest(
                phone="254711222333",
                loss_type="earthquake",
                description="Not a covered peril"
            ))
        assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT

    def test_concurrent_ussd_requests(self, ussd_stub):
        """Simulate multiple simultaneous USSD sessions."""
        results = []
        errors = []

        def make_request(phone):
            try:
                r = ussd_stub.GetPolicyStatus(bimagrid_pb2.PolicyStatusRequest(phone=phone))
                results.append(r)
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=make_request, args=(f"25470000000{i}",)) for i in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert len(results) == 10
