// SPDX-License-Identifier: Apache-2.0
pragma solidity ^0.8.0;

import "./interfaces/IProofOfAction.sol";

/**
 * @title Oracle
 * @dev Multisig verification authority for Proof-of-Action protocol
 * 
 * Architecture:
 * - k-of-n threshold signature scheme
 * - Timelock for parameter changes (48 hours default)
 * - Owner-controlled signer management
 * - Coordinates minting and proof registration
 * 
 * Security Model:
 * - Requires k valid signatures to execute minting
 * - Each signature attests to deterministic verification: Valid(a) ⟺ H(output(a)) = h_chain(a)
 * - Prevents replay attacks via nonce-based request IDs
 */
contract Oracle is IOracle {
    uint256 public constant TIMELOCK_DURATION = 48 hours;

    IMikoToken public token;
    IProofRegistry public registry;
    address public owner;

    mapping(address => bool) private _signers;
    address[] private _signerList;
    uint256 public threshold;

    // Pending parameter changes (timelock)
    struct PendingThreshold {
        uint256 value;
        uint256 effectiveTime;
        bool pending;
    }
    PendingThreshold public pendingThreshold;

    // Request tracking (prevents replay)
    mapping(bytes32 => bool) private _executedRequests;
    uint256 private _nonce;

    modifier onlyOwner() {
        require(msg.sender == owner, "Oracle: caller is not owner");
        _;
    }

    constructor(
        address _token,
        address _registry,
        address[] memory initialSigners,
        uint256 _threshold
    ) {
        require(_token != address(0), "Oracle: token is zero address");
        require(_registry != address(0), "Oracle: registry is zero address");
        require(initialSigners.length >= _threshold, "Oracle: threshold exceeds signer count");
        require(_threshold > 0, "Oracle: threshold must be positive");

        token = IMikoToken(_token);
        registry = IProofRegistry(_registry);
        owner = msg.sender;
        threshold = _threshold;

        for (uint256 i = 0; i < initialSigners.length; i++) {
            address signer = initialSigners[i];
            require(signer != address(0), "Oracle: signer is zero address");
            require(!_signers[signer], "Oracle: duplicate signer");
            
            _signers[signer] = true;
            _signerList.push(signer);
            emit SignerAdded(signer, block.timestamp);
        }
    }

    /**
     * @dev Verifies action and mints tokens with k-of-n threshold signatures
     * @param actor Address that performed the verified action
     * @param amount Token reward for the action
     * @param proofHash Unique hash commitment of the action output
     * @param signatures Array of ECDSA signatures from authorized signers
     * @return requestId Unique identifier for this verification request
     * 
     * Verification Process:
     * 1. Generate unique request ID from parameters
     * 2. Validate k valid signatures from distinct signers
     * 3. Register proof in ProofRegistry
     * 4. Mint tokens to actor via MikoToken contract
     */
    function verifyAndMint(
        address actor,
        uint256 amount,
        bytes32 proofHash,
        bytes[] calldata signatures
    ) external override onlyOwner returns (bytes32 requestId) {
        require(actor != address(0), "Oracle: actor is zero address");
        require(proofHash != bytes32(0), "Oracle: invalid proof hash");
        require(signatures.length >= threshold, "Oracle: insufficient signatures");

        // Generate unique request ID
        requestId = keccak256(abi.encodePacked(
            actor,
            amount,
            proofHash,
            _nonce++,
            block.timestamp
        ));
        require(!_executedRequests[requestId], "Oracle: request already executed");

        // Verify threshold signatures
        bytes32 messageHash = keccak256(abi.encodePacked(
            "\x19Ethereum Signed Message:\n32",
            keccak256(abi.encodePacked(actor, amount, proofHash))
        ));

        address[] memory recoveredSigners = new address[](signatures.length);
        uint256 validSignatures = 0;

        for (uint256 i = 0; i < signatures.length && validSignatures < threshold; i++) {
            address signer = _recoverSigner(messageHash, signatures[i]);
            
            if (_signers[signer] && !_isDuplicate(signer, recoveredSigners, validSignatures)) {
                recoveredSigners[validSignatures] = signer;
                validSignatures++;
                emit VerificationSubmitted(requestId, actor, amount, proofHash, signer);
            }
        }

        require(validSignatures >= threshold, "Oracle: threshold not met");

        // Mark request as executed
        _executedRequests[requestId] = true;

        // Register proof on-chain
        registry.registerProof(proofHash, actor, "verified-action", block.timestamp);

        // Mint tokens
        token.mint(actor, amount, proofHash);

        emit MintExecuted(requestId, actor, amount, proofHash);
    }

    /**
     * @dev Adds a new authorized signer
     */
    function addSigner(address signer) external onlyOwner {
        require(signer != address(0), "Oracle: signer is zero address");
        require(!_signers[signer], "Oracle: signer already exists");

        _signers[signer] = true;
        _signerList.push(signer);
        emit SignerAdded(signer, block.timestamp);
    }

    /**
     * @dev Removes an authorized signer
     */
    function removeSigner(address signer) external onlyOwner {
        require(_signers[signer], "Oracle: signer does not exist");
        require(_signerList.length - 1 >= threshold, "Oracle: would break threshold");

        _signers[signer] = false;
        
        // Remove from list
        for (uint256 i = 0; i < _signerList.length; i++) {
            if (_signerList[i] == signer) {
                _signerList[i] = _signerList[_signerList.length - 1];
                _signerList.pop();
                break;
            }
        }

        emit SignerRemoved(signer, block.timestamp);
    }

    /**
     * @dev Proposes a new threshold (timelock applied)
     */
    function proposeThresholdUpdate(uint256 newThreshold) external onlyOwner {
        require(newThreshold > 0, "Oracle: threshold must be positive");
        require(newThreshold <= _signerList.length, "Oracle: threshold exceeds signer count");

        pendingThreshold = PendingThreshold({
            value: newThreshold,
            effectiveTime: block.timestamp + TIMELOCK_DURATION,
            pending: true
        });

        emit ThresholdUpdated(threshold, newThreshold, pendingThreshold.effectiveTime);
    }

    /**
     * @dev Executes pending threshold update after timelock
     */
    function executeThresholdUpdate() external onlyOwner {
        require(pendingThreshold.pending, "Oracle: no pending threshold");
        require(block.timestamp >= pendingThreshold.effectiveTime, "Oracle: timelock not expired");

        threshold = pendingThreshold.value;
        pendingThreshold.pending = false;
    }

    // ==================== View Functions ====================

    function isSigner(address account) external view override returns (bool) {
        return _signers[account];
    }

    function getThreshold() external view override returns (uint256) {
        return threshold;
    }

    function getSignerCount() external view override returns (uint256) {
        return _signerList.length;
    }

    function getSigners() external view returns (address[] memory) {
        return _signerList;
    }

    // ==================== Internal Functions ====================

    function _recoverSigner(bytes32 messageHash, bytes memory signature) internal pure returns (address) {
        require(signature.length == 65, "Oracle: invalid signature length");

        bytes32 r;
        bytes32 s;
        uint8 v;

        assembly {
            r := mload(add(signature, 32))
            s := mload(add(signature, 64))
            v := byte(0, mload(add(signature, 96)))
        }

        if (v < 27) {
            v += 27;
        }

        require(v == 27 || v == 28, "Oracle: invalid signature v value");

        return ecrecover(messageHash, v, r, s);
    }

    function _isDuplicate(address signer, address[] memory list, uint256 count) internal pure returns (bool) {
        for (uint256 i = 0; i < count; i++) {
            if (list[i] == signer) {
                return true;
            }
        }
        return false;
    }
}
