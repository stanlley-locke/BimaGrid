from unittest.mock import patch
import pytest

from integrations.blockchain import BlockchainClient


class TestBlockchainClient:
    @patch("integrations.blockchain.requests.post")
    def test_eth_call_success(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "0x0000000000000000000000000000000000000000000000000000000000000001",
            "id": 1
        }
        
        client = BlockchainClient()
        result = client.eth_call(
            to_address="0x5FbDB2315678afecb367f032d93F642f64180aa3",
            data="0x06060606"
        )
        
        assert result == "0x0000000000000000000000000000000000000000000000000000000000000001"
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]["json"]
        assert call_args["method"] == "eth_call"
        assert call_args["params"][0]["to"] == "0x5FbDB2315678afecb367f032d93F642f64180aa3"

    @patch("integrations.blockchain.requests.post")
    def test_blockchain_rpc_error(self, mock_post):
        mock_response = mock_post.return_value
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "error": {"code": -32601, "message": "Method not found"},
            "id": 1
        }
        
        client = BlockchainClient()
        result = client.call("non_existent_method")
        assert result is None
