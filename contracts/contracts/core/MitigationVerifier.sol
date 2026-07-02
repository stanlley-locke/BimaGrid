// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

contract MitigationVerifier is Ownable {
    // Mapping of policyId => list of verified mitigation techniques
    mapping(uint256 => string[]) private _policyMitigations;
    
    // Mapping of mitigation technique => discount percentage (scaled by 100, e.g., 1500 = 15%)
    mapping(string => uint256) public mitigationDiscounts;

    event MitigationVerified(uint256 indexed policyId, string mitigationType);
    event DiscountUpdated(string mitigationType, uint256 discountPercent);

    constructor() {
        // Set default discounts
        mitigationDiscounts["drip_irrigation"] = 1500; // 15%
        mitigationDiscounts["soil_bunds"] = 1000;       // 10%
        mitigationDiscounts["mulching"] = 500;          // 5%
    }

    function setMitigationDiscount(string calldata mitigationType, uint256 discountPercent) external onlyOwner {
        require(discountPercent <= 10000, "Discount cannot exceed 100%");
        mitigationDiscounts[mitigationType] = discountPercent;
        emit DiscountUpdated(mitigationType, discountPercent);
    }

    function verifyMitigation(uint256 policyId, string calldata mitigationType) external onlyOwner {
        _policyMitigations[policyId].push(mitigationType);
        emit MitigationVerified(policyId, mitigationType);
    }

    function getPolicyMitigations(uint256 policyId) external view returns (string[] memory) {
        return _policyMitigations[policyId];
    }

    function calculateDiscount(uint256 policyId) external view returns (uint256) {
        string[] memory mitigations = _policyMitigations[policyId];
        uint256 totalDiscount = 0;
        for (uint256 i = 0; i < mitigations.length; i++) {
            totalDiscount += mitigationDiscounts[mitigations[i]];
        }
        if (totalDiscount > 5000) {
            totalDiscount = 5000; // Cap total discount at 50%
        }
        return totalDiscount;
    }
}
