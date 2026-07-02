"""gRPC client for the BimaGrid Django backend."""

from __future__ import annotations

import logging
import grpc
from django.conf import settings

from src.grpc_services import bimagrid_pb2
from src.grpc_services import bimagrid_pb2_grpc

logger = logging.getLogger(__name__)


class GrpcBackendAPIError(Exception):
    pass


class GrpcBackendClient:
    """gRPC Client for USSD internal backend endpoints."""

    def __init__(self, target: str | None = None) -> None:
        self.target = target or getattr(settings, "GRPC_BACKEND_TARGET", "localhost:50051")
        self.channel = grpc.insecure_channel(self.target)
        self.stub = bimagrid_pb2_grpc.UssdServiceStub(self.channel)

    def register_farmer(
        self,
        phone: str,
        ward_code: str,
        crop: str,
        acreage: str | float,
        mpesa_number: str,
    ) -> dict[str, str]:
        request = bimagrid_pb2.RegisterFarmerRequest(
            phone=phone,
            ward_code=ward_code,
            crop=crop,
            acreage=str(acreage),
            mpesa_number=mpesa_number,
        )
        try:
            response = self.stub.RegisterFarmer(request)
            if not response.success:
                raise GrpcBackendAPIError(response.message)
            return {"message": response.message, "policy_number": response.policy_number}
        except grpc.RpcError as e:
            logger.exception("gRPC register_farmer failed")
            raise GrpcBackendAPIError(f"Backend unavailable: {e.details()}")

    def get_policy_status(self, phone: str) -> dict[str, str]:
        request = bimagrid_pb2.PolicyStatusRequest(phone=phone)
        try:
            response = self.stub.GetPolicyStatus(request)
            if not response.success:
                raise GrpcBackendAPIError(response.message)
            return {"status": response.status, "next_payment_date": response.next_payment_date}
        except grpc.RpcError as e:
            logger.exception("gRPC get_policy_status failed")
            raise GrpcBackendAPIError(f"Backend unavailable: {e.details()}")

    def file_claim(self, phone: str, loss_type: str = "drought", description: str = "") -> dict[str, str]:
        request = bimagrid_pb2.FileClaimRequest(
            phone=phone,
            loss_type=loss_type,
            description=description,
        )
        try:
            response = self.stub.FileClaim(request)
            if not response.success:
                raise GrpcBackendAPIError(response.message)
            return {"message": response.message, "claim_reference": response.claim_reference}
        except grpc.RpcError as e:
            logger.exception("gRPC file_claim failed")
            raise GrpcBackendAPIError(f"Backend unavailable: {e.details()}")


_default_grpc_client: GrpcBackendClient | None = None

def get_grpc_backend_client() -> GrpcBackendClient:
    global _default_grpc_client
    if _default_grpc_client is None:
        _default_grpc_client = GrpcBackendClient()
    return _default_grpc_client
