use reqwest::Client;
use serde::Serialize;
use std::error::Error;

#[derive(Debug, Serialize)]
pub struct OraclePayload {
    pub oracle_id: String,
    pub h3_index: String,
    pub timestamp: String,
    pub rainfall_mm: f64,
    pub ndvi: f64,
    pub soil_moisture: f64,
    pub data_sources: Vec<String>,
}

pub async fn submit_to_backend(
    backend_url: &str,
    payload: &OraclePayload,
    signature: &str,
) -> Result<(), Box<dyn Error>> {
    let client = Client::new();
    let url = format!("{}/api/oracles/submit-data/", backend_url.trim_end_matches('/'));

    let response = client
        .post(&url)
        .header("X-Oracle-Signature", signature)
        .header("Content-Type", "application/json")
        .json(payload)
        .send()
        .await?;

    if response.status().is_success() {
        Ok(())
    } else {
        let status = response.status();
        let body = response.text().await.unwrap_or_default();
        Err(format!("Backend submission failed: HTTP {} - {}", status, body).into())
    }
}
