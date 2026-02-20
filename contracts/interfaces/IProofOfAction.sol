// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

/**
 * @title IProofOfAction
 * @dev Interface for Proof-of-Action protocol components
 */

interface IMikoToken {
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 amount, bytes32 indexed proofHash);
    event Burn(address indexed from, uint256 amount);
    event OracleUpdated(address indexed oldOracle, address indexed newOracle);

    function totalSupply() external view returns (uint256);
    function balanceOf(address account) external view returns (uint256);
    function transfer(address to, uint256 amount) external returns (bool);
    function allowance(address owner, address spender) external view returns (uint256);
    function approve(address spender, uint256 amount) external returns (bool);
    function transferFrom(address from, address to, uint256 amount) external returns (bool);
    function mint(address to, uint256 amount, bytes32 proofHash) external;
    function burn(uint256 amount) external;
    function isProofUsed(bytes32 proofHash) external view returns (bool);
}

interface IProofRegistry {
    event ProofRegistered(
        bytes32 indexed proofHash,
        address indexed actor,
        string actionType,
        uint256 timestamp
    );

    struct Proof {
        address actor;
        string actionType;
        uint256 timestamp;
        bool exists;
    }

    function registerProof(
        bytes32 proofHash,
        address actor,
        string calldata actionType,
        uint256 timestamp
    ) external;

    function getProof(bytes32 proofHash) external view returns (
        address actor,
        string memory actionType,
        uint256 timestamp,
        bool exists
    );

    function isProofRegistered(bytes32 proofHash) external view returns (bool);
}

interface IOracle {
    event VerificationSubmitted(
        bytes32 indexed requestId,
        address indexed actor,
        uint256 amount,
        bytes32 indexed proofHash,
        address signer
    );
    event MintExecuted(
        bytes32 indexed requestId,
        address indexed actor,
        uint256 amount,
        bytes32 indexed proofHash
    );
    event SignerAdded(address indexed signer, uint256 timestamp);
    event SignerRemoved(address indexed signer, uint256 timestamp);
    event ThresholdUpdated(uint256 oldThreshold, uint256 newThreshold, uint256 effectiveTime);

    function verifyAndMint(
        address actor,
        uint256 amount,
        bytes32 proofHash,
        bytes[] calldata signatures
    ) external returns (bytes32 requestId);

    function isSigner(address account) external view returns (bool);
    function getThreshold() external view returns (uint256);
    function getSignerCount() external view returns (uint256);
}
