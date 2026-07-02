import sys
import os
import time
import subprocess
import threading

# Add directories to path
sys.path.append(os.path.abspath('backend'))
sys.path.append(os.path.abspath('ussd'))

def run_server():
    print("Starting gRPC server...")
    subprocess.run(["python3", "backend/manage.py", "run_grpc_server"])

server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

time.sleep(3) # Wait for server to start

try:
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "src.config.settings")
    django.setup()
    
    from ussd.src.services.grpc_backend_client import get_grpc_backend_client
    
    print("Connecting USSD gRPC client...")
    client = get_grpc_backend_client()
    
    print("Testing GetPolicyStatus...")
    status_response = client.get_policy_status("254700000000")
    print(f"Status Response: {status_response}")
    
    print("Testing RegisterFarmer...")
    reg_response = client.register_farmer("254700000000", "WARD-123", "MAIZE", 2.5, "254700000000")
    print(f"Register Response: {reg_response}")
    
    print("gRPC Test Successful!")
except Exception as e:
    print(f"gRPC Test Failed: {e}")
    sys.exit(1)
