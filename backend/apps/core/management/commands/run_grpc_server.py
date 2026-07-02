from django.core.management.base import BaseCommand
import grpc
from concurrent import futures
import logging
from apps.grpc_services import bimagrid_pb2
from apps.grpc_services import bimagrid_pb2_grpc

# In a real scenario, you'd import the real services.
# Here we implement mock/demo handlers that would wire to Django services.

class OracleServiceServicer(bimagrid_pb2_grpc.OracleServiceServicer):
    def SubmitData(self, request, context):
        logging.info(f"gRPC Received Oracle Data from {request.oracle_id} for H3 {request.h3_index}")
        return bimagrid_pb2.OracleDataResponse(
            success=True,
            message="Oracle data received and verified via gRPC."
        )

class UssdServiceServicer(bimagrid_pb2_grpc.UssdServiceServicer):
    def RegisterFarmer(self, request, context):
        logging.info(f"gRPC Received Farmer Registration for {request.phone}")
        return bimagrid_pb2.RegisterFarmerResponse(
            success=True,
            message="Farmer registered successfully via gRPC.",
            policy_number="POL-GRPC-123"
        )
        
    def GetPolicyStatus(self, request, context):
        return bimagrid_pb2.PolicyStatusResponse(
            success=True,
            message="Status retrieved via gRPC.",
            status="ACTIVE",
            next_payment_date="2027-01-01"
        )
        
    def FileClaim(self, request, context):
        return bimagrid_pb2.FileClaimResponse(
            success=True,
            message="Claim filed via gRPC.",
            claim_reference="CLM-GRPC-456"
        )

class Command(BaseCommand):
    help = 'Runs the gRPC server for Oracle and USSD communication'

    def handle(self, *args, **options):
        server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        bimagrid_pb2_grpc.add_OracleServiceServicer_to_server(OracleServiceServicer(), server)
        bimagrid_pb2_grpc.add_UssdServiceServicer_to_server(UssdServiceServicer(), server)
        
        port = '[::]:50051'
        server.add_insecure_port(port)
        self.stdout.write(self.style.SUCCESS(f'Starting gRPC server on {port}'))
        server.start()
        server.wait_for_termination()
