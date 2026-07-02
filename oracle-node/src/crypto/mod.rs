use ethers::prelude::*;
use ethers::utils::keccak256;
use ethers::abi::Token;

pub fn parse_h3_index(h3_str: &str) -> [u8; 32] {
    let mut h3_bytes = [0u8; 32];
    let mut clean = h3_str.trim_start_matches("0x").to_string();
    if clean.len() % 2 != 0 {
        clean = format!("0{}", clean);
    }
    if let Ok(decoded) = hex::decode(&clean) {
        let len = decoded.len().min(32);
        let start_idx = 32 - len;
        h3_bytes[start_idx..].copy_from_slice(&decoded[..len]);
    } else {
        let bytes = clean.as_bytes();
        let len = bytes.len().min(32);
        let start_idx = 32 - len;
        h3_bytes[start_idx..].copy_from_slice(&bytes[..len]);
    }
    h3_bytes
}

pub fn hash_payload(
    h3_index: [u8; 32],
    timestamp: u64,
    rainfall: u64,
    ndvi: u64,
) -> [u8; 32] {
    let payload = ethers::abi::encode_packed(&[
        Token::FixedBytes(h3_index.to_vec()),
        Token::Uint(timestamp.into()),
        Token::Uint(rainfall.into()),
        Token::Uint(ndvi.into()),
    ]).expect("Failed to encode packed payload");
    keccak256(&payload)
}

pub async fn sign_payload(
    wallet: &LocalWallet,
    hash: [u8; 32],
) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let signature = wallet.sign_hash(H256::from(hash))?;
    // ethers::types::Signature to_vec() output is 65 bytes
    Ok(signature.to_vec())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_h3_index() {
        let h3_str = "8928308280fffff";
        let parsed = parse_h3_index(h3_str);
        assert_ne!(parsed, [0u8; 32]);

        let h3_hex = "0x8928308280fffff";
        let parsed_hex = parse_h3_index(h3_hex);
        assert_eq!(parsed, parsed_hex);
    }

    #[tokio::test]
    async fn test_hashing_and_signing() {
        let h3_bytes = parse_h3_index("8928308280fffff");
        let timestamp = 1680000000;
        let rainfall = 1500;
        let ndvi = 5000;
        
        let hash = hash_payload(h3_bytes, timestamp, rainfall, ndvi);
        assert_ne!(hash, [0u8; 32]);

        // Create a random wallet for testing
        let wallet = LocalWallet::new(&mut rand::thread_rng());
        let signature = sign_payload(&wallet, hash).await.unwrap();
        assert_eq!(signature.len(), 65);
    }
}

