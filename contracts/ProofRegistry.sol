// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "./interfaces/IProofOfAction.sol";

/**
 * @title ProofRegistry
 * @dev On-chain storage for verified action proofs
 * 
 * Stores immutable records of verified actions including:
 * - Actor address (who performed the action)
 * - Action type (category of productive work)
 * - Timestamp (when the action was verified)
 * - Proof hash (unique collision-resistant identifier)
 * 
 * Ensures:
 * - No duplicate proof registration
 * - Permanent provenance trail
 * - Queryable by proof hash
 */
contract ProofRegistry is IProofRegistry {
    mapping(bytes32 => Proof) private _proofs;
    address public oracle;
    address public owner;

    modifier onlyOracle() {
        require(msg.sender == oracle, "ProofRegistry: caller is not oracle");
        _;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "ProofRegistry: caller is not owner");
        _;
    }

    constructor(address _oracle) {
        require(_oracle != address(0), "ProofRegistry: oracle is zero address");
        oracle = _oracle;
        owner = msg.sender;
    }

    /**
     * @dev Registers a verified action proof on-chain
     * @param proofHash Unique hash of the verified action output
     * @param actor Address of the entity that performed the action
     * @param actionType Category of productive work (e.g., "compute", "data-annotation")
     * @param timestamp Unix timestamp when the action was verified
     * 
     * Requirements:
     * - Caller must be authorized oracle
     * - Proof hash must not already be registered
     * - Proof hash must not be zero
     */
    function registerProof(
        bytes32 proofHash,
        address actor,
        string calldata actionType,
        uint256 timestamp
    ) external override onlyOracle {
        require(proofHash != bytes32(0), "ProofRegistry: invalid proof hash");
        require(!_proofs[proofHash].exists, "ProofRegistry: proof already registered");
        require(actor != address(0), "ProofRegistry: actor is zero address");
        require(bytes(actionType).length > 0, "ProofRegistry: empty action type");

        _proofs[proofHash] = Proof({
            actor: actor,
            actionType: actionType,
            timestamp: timestamp,
            exists: true
        });

        emit ProofRegistered(proofHash, actor, actionType, timestamp);
    }

    /**
     * @dev Retrieves proof details by hash
     * @param proofHash The unique proof identifier
     * @return actor Address who performed the action
     * @return actionType Category of work performed
     * @return timestamp When the action was verified
     * @return exists Whether the proof is registered
     */
    function getProof(bytes32 proofHash) external view override returns (
        address actor,
        string memory actionType,
        uint256 timestamp,
        bool exists
    ) {
        Proof memory proof = _proofs[proofHash];
        return (proof.actor, proof.actionType, proof.timestamp, proof.exists);
    }

    /**
     * @dev Checks if a proof hash has been registered
     * @param proofHash The proof identifier to check
     * @return True if the proof exists in the registry
     */
    function isProofRegistered(bytes32 proofHash) external view override returns (bool) {
        return _proofs[proofHash].exists;
    }

    /**
     * @dev Updates the authorized oracle address
     * @param newOracle New oracle contract address
     */
    function updateOracle(address newOracle) external onlyOwner {
        require(newOracle != address(0), "ProofRegistry: new oracle is zero address");
        oracle = newOracle;
    }
}
