// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IPolicy {
    function registerPolicy(
        uint256 policyId,
        address farmer,
        bytes32 h3Index,
        uint256 threshold,
        uint256 payoutAmount
    ) external;

    function deactivatePolicy(uint256 policyId) external;

    function markPaidOut(uint256 policyId) external;

    function getPolicy(uint256 policyId) external view returns (
        uint256 id,
        address farmer,
        bytes32 h3Index,
        uint256 threshold,
        uint256 payoutAmount,
        bool isActive,
        bool paidOut
    );

    function getPoliciesByH3(bytes32 h3Index) external view returns (uint256[] memory);
}
