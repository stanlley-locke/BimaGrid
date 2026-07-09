"""Blockchain interactions for BimaGrid."""
import json
import logging
from pathlib import Path

from django.conf import settings
from web3 import Web3

logger = logging.getLogger(__name__)

# Usually you would have these in settings or .env
RPC_URL = getattr(settings, "WEB3_RPC_URL", "http://127.0.0.1:8545")
CONTRACT_ADDRESS = getattr(settings, "BIMAGRID_POLICY_ADDRESS", "0x0000000000000000000000000000000000000000") # placeholder
ORACLE_PRIVATE_KEY = getattr(settings, "WEB3_ORACLE_PRIVATE_KEY", "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80") # hardhat account 0 default

def get_web3() -> Web3:
    return Web3(Web3.HTTPProvider(RPC_URL))

def get_contract_abi() -> dict:
    # Path to hardhat compiled artifact
    base_dir = settings.BASE_DIR.parent
    artifact_path = base_dir / "contracts" / "artifacts" / "contracts" / "core" / "BimaGridPolicy.sol" / "BimaGridPolicy.json"
    try:
        with open(artifact_path, "r") as f:
            data = json.load(f)
            return data.get("abi", [])
    except Exception as e:
        logger.error(f"Could not load ABI: {e}")
        return []

def trigger_smart_contract_payout(policy_id: int):
    """Trigger a payout on the smart contract for the given policy ID."""
    w3 = get_web3()
    if not w3.is_connected():
        logger.error("Web3 is not connected to RPC: %s", RPC_URL)
        return False
        
    abi = get_contract_abi()
    if not abi:
        return False
        
    contract = w3.eth.contract(address=w3.to_checksum_address(CONTRACT_ADDRESS), abi=abi)
    account = w3.eth.account.from_key(ORACLE_PRIVATE_KEY)
    
    try:
        transaction = contract.functions.triggerPayout(policy_id).build_transaction({
            'chainId': w3.eth.chain_id,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        signed_txn = w3.eth.account.sign_transaction(transaction, private_key=ORACLE_PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        logger.info(f"Payout triggered on-chain for policy {policy_id}. TX Hash: {w3.to_hex(tx_hash)}")
        
        # Wait for receipt
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        if receipt.status == 1:
            logger.info("Transaction successful!")
            return True
        else:
            logger.error("Transaction failed on-chain.")
            return False
            
    except Exception as e:
        logger.error(f"Error triggering payout on chain: {e}")
        return False
