// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

/// @title EscrowVault — Holds farmer premiums and executes parametric payouts.
/// @notice Uses custom errors (EIP-838) for 4-byte revert selectors over costly string reverts.
///         Pull-payment pattern used for refunds to separate ETH flow from accounting.
contract EscrowVault is Ownable, ReentrancyGuard {

    // policyId => deposited premium (uint128 saves one slot vs uint256 when co-stored)
    mapping(uint256 => uint128) public premiums;

    // Pending refunds: farmer => claimable balance (pull-payment safety pattern)
    mapping(address => uint256) public pendingRefunds;

    mapping(address => bool) public authorizedCallers;

    event PremiumDeposited(uint256 indexed policyId, uint128 amount);
    event PayoutExecuted(uint256 indexed policyId, address indexed farmer, uint256 amount);
    event RefundPending(uint256 indexed policyId, address indexed farmer, uint256 amount);
    event RefundClaimed(address indexed farmer, uint256 amount);
    event CallerAuthorized(address caller, bool authorized);

    error NotAuthorized();
    error ZeroAmount();
    error ZeroAddress();
    error InsufficientBalance(uint256 requested, uint256 available);
    error NoPendingRefund();
    error TransferFailed();

    modifier onlyAuthorized() {
        if (msg.sender != owner() && !authorizedCallers[msg.sender]) revert NotAuthorized();
        _;
    }

    function setAuthorizedCaller(address caller, bool authorized) external onlyOwner {
        authorizedCallers[caller] = authorized;
        emit CallerAuthorized(caller, authorized);
    }

    function depositPremium(uint256 policyId) external payable {
        if (msg.value == 0) revert ZeroAmount();
        // Safe: msg.value fits uint128 for KES-denominated sub-ETH amounts
        premiums[policyId] += uint128(msg.value);
        emit PremiumDeposited(policyId, uint128(msg.value));
    }

    /// @dev Push-payment payout for parametric claim settlements.
    ///      nonReentrant guard prevents re-entrancy on the .call{value} transfer.
    function payout(
        uint256 policyId,
        address payable farmer,
        uint256 amount
    ) external onlyAuthorized nonReentrant {
        if (farmer == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        uint256 bal = address(this).balance;
        if (bal < amount) revert InsufficientBalance(amount, bal);

        (bool success, ) = farmer.call{value: amount}("");
        if (!success) revert TransferFailed();

        emit PayoutExecuted(policyId, farmer, amount);
    }

    /// @dev Pull-payment refund: credits farmer's pending balance.
    ///      Farmer must call claimRefund() to receive ETH.
    ///      This eliminates push-transfer vulnerabilities entirely.
    function refundPremium(
        uint256 policyId,
        address farmer,
        uint256 amount
    ) external onlyAuthorized {
        if (farmer == address(0)) revert ZeroAddress();
        if (amount == 0) revert ZeroAmount();
        pendingRefunds[farmer] += amount;
        emit RefundPending(policyId, farmer, amount);
    }

    /// @dev Farmers call this directly to withdraw their pending refund balance.
    function claimRefund() external nonReentrant {
        uint256 amount = pendingRefunds[msg.sender];
        if (amount == 0) revert NoPendingRefund();

        // Zero-before-transfer to prevent re-entrancy
        pendingRefunds[msg.sender] = 0;

        (bool success, ) = payable(msg.sender).call{value: amount}("");
        if (!success) revert TransferFailed();

        emit RefundClaimed(msg.sender, amount);
    }

    receive() external payable {}
}
