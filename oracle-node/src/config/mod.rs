use serde::Deserialize;
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
        let config: Config = toml::from_str(&content)?;
        Ok(config)
    }
}
