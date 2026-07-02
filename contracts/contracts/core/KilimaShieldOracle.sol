// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "./PolicyRegistry.sol";
import "./EscrowVault.sol";
import "../libraries/ECDSA.sol";
import "../libraries/H3.sol";

/// @title KilimaShieldOracle — Multi-sig parametric trigger engine.
/// @notice Gas-optimized: packed structs (single SSTORE), calldata signatures,
///         custom errors (EIP-838), cached storage reads, and efficient median.
contract KilimaShieldOracle is Ownable {

    // ─── Packed Struct (fits in 1 storage slot: 128+112+8 = 248 bits ≤ 256) ─
    struct DataPayload {
        uint128 rainfall;
        uint112 ndvi;
        bool exists;
    }

    PolicyRegistry public policyRegistry;
    EscrowVault public escrowVault;

    mapping(address => bool) public isAuthorizedOracle;
    uint256 public oracleCount;

    // h3Index => timestamp => oracleAddress => DataPayload
    mapping(bytes32 => mapping(uint256 => mapping(address => DataPayload))) public submissions;
    // h3Index => timestamp => submitter list
    mapping(bytes32 => mapping(uint256 => address[])) public submitters;

    // ─── Custom Errors (4-byte selectors, cheaper than string reverts) ────────
    error ZeroAddress();
    error InvalidH3Index(bytes32 h3Index);
    error UnauthorizedOracle(address signer);
    error DuplicateSubmission(address oracle, bytes32 h3Index, uint256 timestamp);
    error InvalidOracleAddress();
    error PremiumRequired();

    // ─── Events ───────────────────────────────────────────────────────────────
    event PolicyRegistered(uint256 indexed policyId, address indexed farmer, bytes32 indexed h3Index);
    event DataSubmitted(address indexed oracle, bytes32 indexed h3Index, uint256 timestamp);
    event ConsensusReached(bytes32 indexed h3Index, uint256 timestamp, uint256 medianRainfall, uint256 medianNdvi);
    event PayoutTriggered(uint256 indexed policyId, address indexed farmer, uint256 amount);
    event OracleAuthorized(address indexed oracle, bool authorized);

    constructor(address _policyRegistry, address payable _escrowVault) {
        if (_policyRegistry == address(0)) revert ZeroAddress();
        if (_escrowVault == address(0)) revert ZeroAddress();
        policyRegistry = PolicyRegistry(_policyRegistry);
        escrowVault = EscrowVault(_escrowVault);
    }

    function setAuthorizedOracle(address oracle, bool authorized) external onlyOwner {
        if (oracle == address(0)) revert InvalidOracleAddress();
        if (authorized && !isAuthorizedOracle[oracle]) {
            oracleCount++;
        } else if (!authorized && isAuthorizedOracle[oracle]) {
            oracleCount--;
        }
        isAuthorizedOracle[oracle] = authorized;
        emit OracleAuthorized(oracle, authorized);
    }

    function registerPolicy(
        uint256 policyId,
        address farmer,
        bytes32 h3Index,
        uint128 threshold,
        uint128 payoutAmount
    ) external payable onlyOwner {
        if (!H3.isValidH3Index(h3Index)) revert InvalidH3Index(h3Index);
        if (msg.value == 0) revert PremiumRequired();

        policyRegistry.registerPolicy(policyId, farmer, h3Index, threshold, payoutAmount);
        escrowVault.depositPremium{value: msg.value}(policyId);

        emit PolicyRegistered(policyId, farmer, h3Index);
    }

    function submitData(
        bytes32 h3Index,
        uint256 timestamp,
        uint256 rainfall,
        uint256 ndvi,
        bytes calldata signature          // calldata: avoid memory copy of 65-byte sig
    ) external {
        if (!H3.isValidH3Index(h3Index)) revert InvalidH3Index(h3Index);

        // Recover signer — single keccak + ECDSA recover
        bytes32 messageHash = keccak256(abi.encodePacked(h3Index, timestamp, rainfall, ndvi));
        bytes32 ethSignedHash = ECDSA.toEthSignedMessageHash(messageHash);
        address signer = ECDSA.recover(ethSignedHash, signature);

        if (!isAuthorizedOracle[signer]) revert UnauthorizedOracle(signer);
        if (submissions[h3Index][timestamp][signer].exists)
            revert DuplicateSubmission(signer, h3Index, timestamp);

        // Write packed struct — single SSTORE (248 bits fit in 256-bit slot)
        submissions[h3Index][timestamp][signer] = DataPayload({
            rainfall: uint128(rainfall),
            ndvi: uint112(ndvi),
            exists: true
        });
        submitters[h3Index][timestamp].push(signer);

        emit DataSubmitted(signer, h3Index, timestamp);

        // Trigger consensus evaluation after 3 unique oracle submissions
        if (submitters[h3Index][timestamp].length == 3) {
            _evaluateConsensus(h3Index, timestamp);
        }
    }

    /// @dev Cache the submitters array in memory once — avoids repeated SLOAD
    function _evaluateConsensus(bytes32 h3Index, uint256 timestamp) internal {
        address[] memory oracles = submitters[h3Index][timestamp];

        // Load all payloads from storage — each is 1 SLOAD (packed slot)
        DataPayload memory p0 = submissions[h3Index][timestamp][oracles[0]];
        DataPayload memory p1 = submissions[h3Index][timestamp][oracles[1]];
        DataPayload memory p2 = submissions[h3Index][timestamp][oracles[2]];

        uint256 medianRainfall = _median3(p0.rainfall, p1.rainfall, p2.rainfall);
        uint256 medianNdvi = _median3(p0.ndvi, p1.ndvi, p2.ndvi);

        emit ConsensusReached(h3Index, timestamp, medianRainfall, medianNdvi);
        _evaluatePolicies(h3Index, medianRainfall);
    }

    function _evaluatePolicies(bytes32 h3Index, uint256 medianRainfall) internal {
        uint256[] memory policyIds = policyRegistry.getPoliciesByH3(h3Index);
        uint256 len = policyIds.length;
        for (uint256 i; i < len; ) {
            uint256 policyId = policyIds[i];
            (
                ,
                address farmer,
                ,
                uint128 threshold,
                uint128 payoutAmount,
                bool isActive,
                bool paidOut
            ) = policyRegistry.getPolicy(policyId);

            if (isActive && !paidOut && medianRainfall < threshold) {
                policyRegistry.markPaidOut(policyId);
                escrowVault.payout(policyId, payable(farmer), payoutAmount);
                emit PayoutTriggered(policyId, farmer, payoutAmount);
            }
            unchecked { ++i; }           // save gas: no overflow risk on policy list
        }
    }

    /// @dev Branchless-style 3-value median. Pure function, zero SLOAD.
    function _median3(uint256 a, uint256 b, uint256 c) internal pure returns (uint256) {
        if ((a <= b && b <= c) || (c <= b && b <= a)) return b;
        if ((b <= a && a <= c) || (c <= a && a <= b)) return a;
        return c;
    }

    // ─── Public wrapper kept for test compatibility ───────────────────────────
    function getMedian(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
        return _median3(a, b, c);
    }
}
