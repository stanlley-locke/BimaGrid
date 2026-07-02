use ethers::prelude::*;
use std::sync::Arc;

abigen!(
    KilimaShieldOracleContract,
    "../contracts/artifacts/contracts/core/KilimaShieldOracle.sol/KilimaShieldOracle.json",
    event_derives(serde::Deserialize, serde::Serialize)
);

pub async fn submit_data_to_blockchain(
    rpc_url: &str,
    contract_addr: &str,
    signing_key: &str,
    h3_index: [u8; 32],
    timestamp: u64,
    rainfall: u64,
    ndvi: u64,
    signature: Vec<u8>,
) -> Result<TxHash, Box<dyn std::error::Error>> {
    // 1. Initialize provider and wallet
    let provider = Provider::<Http>::try_from(rpc_url)?;
    // Use Hardhat standard chain ID 31337 (or fallback to 1337)
    let wallet = signing_key.parse::<LocalWallet>()?.with_chain_id(31337u64);
    let client = SignerMiddleware::new(provider, wallet);
    let client = Arc::new(client);

    // 2. Parse contract address
    let address = contract_addr.parse::<Address>()?;
    let contract = KilimaShieldOracleContract::new(address, client);

    // 3. Send transaction
    let tx = contract.submit_data(
        h3_index,
        timestamp.into(),
        rainfall.into(),
        ndvi.into(),
        signature.into(),
    );

    let pending_tx = tx.send().await?;
    let receipt = pending_tx.await?;
    
    match receipt {
        Some(r) => Ok(r.transaction_hash),
        None => Err("Transaction was not mined".into()),
    }
}
