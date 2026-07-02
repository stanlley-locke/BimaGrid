#!/bin/bash
set -e

echo "Generating gRPC Python stubs for BimaGrid..."

# Backend directories
BACKEND_GRPC_DIR="backend/apps/grpc_services"
mkdir -p $BACKEND_GRPC_DIR

# USSD directories
USSD_GRPC_DIR="ussd/src/grpc_services"
mkdir -p $USSD_GRPC_DIR

# Generate for Backend
python3 -m grpc_tools.protoc -I./protos \
    --python_out=$BACKEND_GRPC_DIR \
    --grpc_python_out=$BACKEND_GRPC_DIR \
    ./protos/bimagrid.proto

# Generate for USSD
python3 -m grpc_tools.protoc -I./protos \
    --python_out=$USSD_GRPC_DIR \
    --grpc_python_out=$USSD_GRPC_DIR \
    ./protos/bimagrid.proto

echo "Done! Make sure to update the __init__.py files and fix relative imports if necessary."
