// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IOracle {
    function submitData(
        bytes32 h3Index,
        uint256 timestamp,
        uint256 rainfall,
        uint256 ndvi,
        bytes calldata signature
    ) external;

    function setAuthorizedOracle(address oracle, bool authorized) external;
}
