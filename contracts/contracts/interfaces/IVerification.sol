// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IVerification {
    function setMitigationDiscount(string calldata mitigationType, uint256 discountPercent) external;
    
    function verifyMitigation(uint256 policyId, string calldata mitigationType) external;
    
    function getPolicyMitigations(uint256 policyId) external view returns (string[] memory);
    
    function calculateDiscount(uint256 policyId) external view returns (uint256);
}
