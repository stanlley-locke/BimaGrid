// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract BimaGridPolicy {
    struct Policy {
        address farmer;
        uint256 payoutAmount;
        bool isActive;
    }

    address public owner;
    address public oracleNode;
    
    mapping(uint256 => Policy) public policies;
    uint256 public nextPolicyId = 1;

    event PolicyCreated(uint256 indexed policyId, address indexed farmer, uint256 payoutAmount);
    event PayoutTriggered(uint256 indexed policyId, address indexed farmer, uint256 amount);

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    modifier onlyOracle() {
        require(msg.sender == oracleNode, "Only oracle can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
        oracleNode = msg.sender; // By default, the deployer is the oracle
    }

    function setOracleNode(address _oracleNode) external onlyOwner {
        oracleNode = _oracleNode;
    }

    function createPolicy(address _farmer, uint256 _payoutAmount) external onlyOwner returns (uint256) {
        uint256 policyId = nextPolicyId++;
        policies[policyId] = Policy({
            farmer: _farmer,
            payoutAmount: _payoutAmount,
            isActive: true
        });
        
        emit PolicyCreated(policyId, _farmer, _payoutAmount);
        return policyId;
    }

    function triggerPayout(uint256 _policyId) external onlyOracle {
        Policy storage policy = policies[_policyId];
        require(policy.isActive, "Policy is not active");
        require(policy.payoutAmount > 0, "Payout amount is zero");
        
        policy.isActive = false;
        
        emit PayoutTriggered(_policyId, policy.farmer, policy.payoutAmount);
    }
}
