use serde::Deserialize;
use std::env;
use std::fs;
use std::path::Path;

#[derive(Debug, Deserialize, Clone)]
pub struct NodeConfig {
    pub id: String,
    pub backend_url: Option<String>,
    pub data_sources: Vec<String>,
    pub signing_key: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct BlockchainConfig {
    pub rpc_url: String,
    pub contract_address: String,
    pub gas_limit: Option<u64>,
}

#[derive(Debug, Deserialize, Clone)]
pub struct ScheduleConfig {
    pub evaluation_time: String,
    pub timezone: String,
}

#[derive(Debug, Deserialize, Clone)]
pub struct Config {
    pub node: NodeConfig,
    pub blockchain: BlockchainConfig,
    pub schedule: ScheduleConfig,
}

impl Config {
    pub fn load_from_file<P: AsRef<Path>>(path: P) -> Result<Self, Box<dyn std::error::Error>> {
        let content = fs::read_to_string(path)?;
        let mut config: Config = toml::from_str(&content)?;
        config.apply_env_overrides();
        Ok(config)
    }

    /// Override TOML values with environment variables (Docker Compose / .env).
    pub fn apply_env_overrides(&mut self) {
        if let Ok(key) = env::var("ORACLE_SIGNING_KEY") {
            if !key.is_empty() {
                self.node.signing_key = key;
            }
        }
        if let Ok(url) = env::var("BLOCKCHAIN_RPC_URL") {
            if !url.is_empty() {
                self.blockchain.rpc_url = url;
            }
        }
        if let Ok(url) = env::var("BACKEND_GRPC_URL") {
            if !url.is_empty() {
                self.node.backend_url = Some(url);
            }
        }
        if let Ok(addr) = env::var("CONTRACT_KILIMA_SHIELD_ORACLE") {
            if !addr.is_empty() && addr != "0x0000000000000000000000000000000000000000" {
                self.blockchain.contract_address = addr;
            }
        }
    }
}
