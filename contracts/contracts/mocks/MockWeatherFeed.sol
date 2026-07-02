// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

contract MockWeatherFeed {
    struct WeatherReport {
        uint256 rainfall;
        uint256 ndvi;
        uint256 timestamp;
    }

    // h3Index => latest WeatherReport
    mapping(bytes32 => WeatherReport) public reports;

    event ReportUpdated(bytes32 indexed h3Index, uint256 rainfall, uint256 ndvi, uint256 timestamp);

    function updateReport(bytes32 h3Index, uint256 rainfall, uint256 ndvi) external {
        reports[h3Index] = WeatherReport({
            rainfall: rainfall,
            ndvi: ndvi,
            timestamp: block.timestamp
        });
        emit ReportUpdated(h3Index, rainfall, ndvi, block.timestamp);
    }
}
