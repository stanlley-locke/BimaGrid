use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct WeatherData {
    pub h3_index: String,
    pub rainfall_mm: f64,
    pub ndvi: f64,
    pub soil_moisture: f64,
}

pub fn h3_to_coords(h3_index: &str) -> (f64, f64) {
    let mut hash = 0u64;
    for c in h3_index.chars() {
        hash = hash.wrapping_add(c as u64);
    }
    let lat = -1.30 + ((hash % 100) as f64 - 50.0) * 0.005;
    let lon = 36.80 + ((hash % 100) as f64 - 50.0) * 0.005;
    (lat, lon)
}

pub async fn fetch_open_meteo_rainfall(lat: f64, lon: f64) -> Result<f64, Box<dyn std::error::Error>> {
    let url = format!(
        "https://api.open-meteo.com/v1/forecast?latitude={:.4}&longitude={:.4}&daily=precipitation_sum&timezone=Africa/Nairobi&past_days=1",
        lat, lon
    );
    let resp = reqwest::Client::new()
        .get(&url)
        .header("User-Agent", "bimagrid-oracle/0.1.0")
        .send()
        .await?
        .json::<serde_json::Value>()
        .await?;
        
    let precips = resp["daily"]["precipitation_sum"]
        .as_array()
        .ok_or("Invalid daily precipitation response")?;
        
    if precips.is_empty() {
        return Ok(0.0);
    }
    
    let sum: f64 = precips
        .iter()
        .map(|v| v.as_f64().unwrap_or(0.0))
        .sum();
    Ok(sum / precips.len() as f64)
}

pub async fn ingest_data(
    h3_index: &str,
    sources: &[String],
) -> Result<WeatherData, Box<dyn std::error::Error>> {
    let (lat, lon) = h3_to_coords(h3_index);
    
    // Fetch Open-Meteo rainfall if configured, otherwise default to a mock value
    let mut rainfall = 12.5; // default base value
    if sources.contains(&"open-meteo".to_string()) {
        if let Ok(val) = fetch_open_meteo_rainfall(lat, lon).await {
            rainfall = val;
        }
    }
    
    // Seed pseudo-random values using H3 index characters
    let mut seed = 0u64;
    for c in h3_index.chars() {
        seed = seed.wrapping_add(c as u64);
    }
    
    // Generate deterministic pseudo-random NDVI and Soil Moisture
    let ndvi = 0.3 + ((seed % 50) as f64) / 100.0; // range [0.3, 0.8]
    let soil_moisture = 0.15 + ((seed % 30) as f64) / 100.0; // range [0.15, 0.45]
    
    Ok(WeatherData {
        h3_index: h3_index.to_string(),
        rainfall_mm: rainfall,
        ndvi,
        soil_moisture,
    })
}
