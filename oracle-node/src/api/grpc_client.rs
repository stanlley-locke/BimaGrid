use bimagrid::oracle_service_client::OracleServiceClient;
use bimagrid::OracleDataRequest;
use std::error::Error;
use tonic::transport::Channel;

pub mod bimagrid {
    tonic::include_proto!("bimagrid");
}

pub struct GrpcBackendClient {
    client: OracleServiceClient<Channel>,
}

impl GrpcBackendClient {
    pub async fn connect(url: String) -> Result<Self, Box<dyn Error>> {
        let client = OracleServiceClient::connect(url).await?;
        Ok(Self { client })
    }

    pub async fn submit_data(
        &mut self,
        oracle_id: String,
        h3_index: String,
        timestamp: u64,
        rainfall_mm: f64,
        ndvi: f64,
        soil_moisture: f64,
        data_sources: Vec<String>,
        signature: String,
    ) -> Result<(), Box<dyn Error>> {
        let request = tonic::Request::new(OracleDataRequest {
            oracle_id,
            h3_index,
            timestamp: timestamp.to_string(),
            rainfall_mm,
            ndvi,
            soil_moisture,
            data_sources,
            signature,
        });

        let response = self.client.submit_data(request).await?;
        
        if response.into_inner().success {
            Ok(())
        } else {
            Err("Backend rejected the gRPC submission payload".into())
        }
    }
}
