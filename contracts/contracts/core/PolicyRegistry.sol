// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";

/// @title PolicyRegistry — Tracks all farmer parametric insurance policies.
/// @notice Optimized for minimal storage: booleans packed alongside uint96 fields.
contract PolicyRegistry is Ownable {

    // ─── Gas-Optimized Struct ────────────────────────────────────────────────
    // Slot 1: id (uint256)
    // Slot 2: farmer (address=20b) + isActive (bool=1b) + paidOut (bool=1b) — packed
    // Slot 3: h3Index (bytes32)
    // Slot 4: threshold (uint128) + payoutAmount (uint128)  — packed into 1 slot
    struct Policy {
        uint256 id;
        address farmer;
        bool isActive;
        bool paidOut;
        bytes32 h3Index;
        uint128 threshold;
        uint128 payoutAmount;
    }

    mapping(uint256 => Policy) public policies;
    mapping(bytes32 => uint256[]) private _h3Policies;
    mapping(address => bool) public authorizedCallers;

    event PolicyRegistered(uint256 indexed policyId, address indexed farmer, bytes32 indexed h3Index);
    event PolicyDeactivated(uint256 indexed policyId);
    event PolicyPaidOut(uint256 indexed policyId);
    event CallerAuthorized(address caller, bool authorized);

    error NotAuthorized();
    error PolicyAlreadyExists(uint256 policyId);
    error PolicyDoesNotExist(uint256 policyId);
    error PolicyNotActive(uint256 policyId);
    error PolicyAlreadyPaidOut(uint256 policyId);
    error ZeroAddress();
    error ZeroPayoutAmount();

    modifier onlyAuthorized() {
        if (msg.sender != owner() && !authorizedCallers[msg.sender]) revert NotAuthorized();
        _;
    }

    function setAuthorizedCaller(address caller, bool authorized) external onlyOwner {
        authorizedCallers[caller] = authorized;
        emit CallerAuthorized(caller, authorized);
    }

    function registerPolicy(
        uint256 policyId,
        address farmer,
        bytes32 h3Index,
        uint128 threshold,
        uint128 payoutAmount
    ) external onlyAuthorized {
        if (policies[policyId].farmer != address(0)) revert PolicyAlreadyExists(policyId);
        if (farmer == address(0)) revert ZeroAddress();
        if (payoutAmount == 0) revert ZeroPayoutAmount();

        // Write entire struct in-order so Solidity packs efficiently
        policies[policyId] = Policy({
            id: policyId,
            farmer: farmer,
            isActive: true,
            paidOut: false,
            h3Index: h3Index,
            threshold: threshold,
            payoutAmount: payoutAmount
        });

        _h3Policies[h3Index].push(policyId);

        emit PolicyRegistered(policyId, farmer, h3Index);
    }

    function deactivatePolicy(uint256 policyId) external onlyAuthorized {
        if (policies[policyId].farmer == address(0)) revert PolicyDoesNotExist(policyId);
        policies[policyId].isActive = false;
        emit PolicyDeactivated(policyId);
    }

    function markPaidOut(uint256 policyId) external onlyAuthorized {
        Policy storage p = policies[policyId];
        if (p.farmer == address(0)) revert PolicyDoesNotExist(policyId);
        if (!p.isActive) revert PolicyNotActive(policyId);
        if (p.paidOut) revert PolicyAlreadyPaidOut(policyId);

        // Single storage slot update — both booleans packed in same slot as farmer address
        p.paidOut = true;
        p.isActive = false;

        emit PolicyPaidOut(policyId);
    }

    function getPolicy(uint256 policyId) external view returns (
        uint256 id,
        address farmer,
        bytes32 h3Index,
        uint128 threshold,
        uint128 payoutAmount,
        bool isActive,
        bool paidOut
    ) {
        Policy storage p = policies[policyId];
        return (p.id, p.farmer, p.h3Index, p.threshold, p.payoutAmount, p.isActive, p.paidOut);
    }

    function getPoliciesByH3(bytes32 h3Index) external view returns (uint256[] memory) {
        return _h3Policies[h3Index];
    }
}
