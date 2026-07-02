// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "../core/KilimaShieldOracle.sol";

contract MockOracle {
    KilimaShieldOracle public oracle;

    constructor(address _oracle) {
        oracle = KilimaShieldOracle(_oracle);
    }

    function submitMockData(
        bytes32 h3Index,
        uint256 timestamp,
        uint256 rainfall,
        uint256 ndvi,
        bytes calldata signature
    ) external {
        oracle.submitData(h3Index, timestamp, rainfall, ndvi, signature);
    }
}
