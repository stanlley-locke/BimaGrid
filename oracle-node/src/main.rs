use std::env;
use std::time::Duration;
use tokio::time;
use bimagrid_oracle::{config, ingestion, crypto, blockchain};

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("Starting BimaGrid Oracle Node...");

    // 1. Get config path from command line arguments
    let args: Vec<String> = env::args().collect();
    let config_path = if args.len() > 2 && args[1] == "--config" {
        args[2].clone()
    } else if args.len() > 1 {
        args[1].clone()
    } else {
        "oracle-config-1.toml".to_string()
    };

    println!("Loading configuration from: {}", config_path);
    let config = match config::Config::load_from_file(&config_path) {
        Ok(c) => c,
        Err(e) => {
            eprintln!("Warning: Failed to load config file: {}. Using fallback defaults.", e);
            // Fallback config for testing/demo (reusable private key)
            config::Config {
                node: config::NodeConfig {
                    id: "oracle-1".to_string(),
                    data_sources: vec!["open-meteo".to_string()],
                    signing_key: "0x47e175b104810481048104810481048104810481048104810481048104810481".to_string(),
                    backend_url: Some("http://localhost:50051".to_string()),
                },
                blockchain: config::BlockchainConfig {
                    rpc_url: "http://localhost:8545".to_string(),
                    contract_address: "0x5FbDB2315678afecb367f032d93F642f64180aa3".to_string(),
                    gas_limit: Some(500000),
                },
                schedule: config::ScheduleConfig {
                    evaluation_time: "23:00".to_string(),
                    timezone: "Africa/Nairobi".to_string(),
                },
            }
        }
    };

    println!("Oracle Node ID: {}", config.node.id);
    println!("Data Sources: {:?}", config.node.data_sources);
    println!("Target RPC: {}", config.blockchain.rpc_url);

    // List of active H3 indices to monitor (default for demo / testing)
    let target_h3_indices = vec![
        "8928308280fffff".to_string(),
        "8928308280ffffe".to_string(),
    ];

    // Running once on startup
    println!("Running initial data collection and submission cycle...");
    run_cycle(&config, &target_h3_indices).await;

    // Start scheduler loop (every 60 seconds for demo/development purposes)
    println!("Starting schedule monitoring loop (triggering every 60s)...");
    let mut interval = time::interval(Duration::from_secs(60));
    // Skip the first tick since we just ran it
    interval.tick().await; 

    loop {
        interval.tick().await;
        println!("Scheduled trigger activated. Starting cycle...");
        run_cycle(&config, &target_h3_indices).await;
    }
}

async fn run_cycle(config: &config::Config, h3_indices: &[String]) {
    let timestamp = chrono::Utc::now().timestamp() as u64;
    println!("Ingesting weather data for timestamp: {}", timestamp);

    for h3_str in h3_indices {
        println!("Processing H3 index: {}", h3_str);
        
        // 1. Ingest
        let weather = match ingestion::ingest_data(h3_str, &config.node.data_sources).await {
            Ok(w) => w,
            Err(e) => {
                eprintln!("Error ingesting weather data for H3 {}: {}", h3_str, e);
                continue;
            }
        };

        println!(
            "Ingested: Rainfall: {:.2}mm, NDVI: {:.4}, Soil Moisture: {:.4}",
            weather.rainfall_mm, weather.ndvi, weather.soil_moisture
        );

        // Scale values to integers (mm * 100, NDVI * 10000) as required by contracts
        let scaled_rainfall = (weather.rainfall_mm * 100.0) as u64;
        let scaled_ndvi = (weather.ndvi * 10000.0) as u64;

        // 2. Hash and Cryptographically Sign Payload
        let h3_bytes = crypto::parse_h3_index(h3_str);
        let hash = crypto::hash_payload(h3_bytes, timestamp, scaled_rainfall, scaled_ndvi);

        // Sign with private key wallet
        let wallet = match config.node.signing_key.parse::<ethers::signers::LocalWallet>() {
            Ok(w) => w,
            Err(e) => {
                eprintln!("Error parsing signing key: {}", e);
                continue;
            }
        };

        let signature = match crypto::sign_payload(&wallet, hash).await {
            Ok(sig) => sig,
            Err(e) => {
                eprintln!("Error signing payload: {}", e);
                continue;
            }
        };

        println!("ECDSA signature generated ({} bytes)", signature.len());

        // 3. Submit to Off-Chain Backend over gRPC
        let sig_hex = format!("0x{}", hex::encode(&signature));
        if let Some(backend_url) = &config.node.backend_url {
            println!("Connecting to gRPC backend API: {}", backend_url);
            match bimagrid_oracle::api::grpc_client::GrpcBackendClient::connect(backend_url.clone()).await {
                Ok(mut grpc_client) => {
                    match grpc_client.submit_data(
                        config.node.id.clone(),
                        h3_str.clone(),
                        timestamp,
                        weather.rainfall_mm,
                        weather.ndvi,
                        weather.soil_moisture,
                        config.node.data_sources.clone(),
                        sig_hex,
                    ).await {
                        Ok(_) => println!("gRPC backend API submission successful."),
                        Err(e) => eprintln!("gRPC backend API submission failed: {}", e),
                    }
                },
                Err(e) => eprintln!("Failed to connect to gRPC backend: {}", e),
            }
        }

        // 4. Submit/Broadcast to Smart Contract
        println!("Broadcasting submission to smart contract: {}", config.blockchain.contract_address);
        match blockchain::submit_data_to_blockchain(
            &config.blockchain.rpc_url,
            &config.blockchain.contract_address,
            &config.node.signing_key,
            h3_bytes,
            timestamp,
            scaled_rainfall,
            scaled_ndvi,
            signature,
        ).await {
            Ok(tx_hash) => {
                println!("Successfully submitted data. Tx Hash: {:?}", tx_hash);
            }
            Err(e) => {
                eprintln!(
                    "Failed to broadcast data for H3 {} to contract. Error: {}. (Note: This is expected if the local Hardhat node/chain is not running)",
                    h3_str, e
                );
            }
        }
    }
}
