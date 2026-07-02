// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

interface IEscrow {
    function depositPremium(uint256 policyId) external payable;
    
    function payout(
        uint256 policyId,
        address payable farmer,
        uint256 amount
    ) external;

    function refundPremium(
        uint256 policyId,
        address payable farmer,
        uint256 amount
    ) external;
}
