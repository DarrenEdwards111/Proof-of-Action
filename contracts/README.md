# Proof-of-Action Reference Implementation

Solidity smart contracts implementing the Proof-of-Action minting policy described in the paper.

## Architecture

The reference implementation consists of three core contracts:

### 1. **MikoToken.sol** — ERC-20 Token with PoAct Minting

Standard fungible token with Proof-of-Action issuance policy:

- **Uncapped Supply**: Tokens minted on-demand upon verified actions (no pre-mine, no cap)
- **Proof Hash Registry**: Each mint requires a unique `bytes32` proof hash; duplicates rejected
- **Oracle Authority**: Only authorized oracle can call `mint()`
- **Burn Function**: Holders can burn tokens, contributing to supply equilibrium
- **Owner Controls**: Owner can update oracle address for governance flexibility

**Key Functions:**
```solidity
mint(address to, uint256 amount, bytes32 proofHash)  // Oracle-only
burn(uint256 amount)                                  // Public
isProofUsed(bytes32 proofHash) → bool                // Query
```

### 2. **ProofRegistry.sol** — On-Chain Proof Storage

Immutable registry of verified action proofs providing complete provenance:

- **Proof Structure**: `(actor, actionType, timestamp, exists)`
- **Duplicate Prevention**: Rejects re-registration of existing proof hashes
- **Permanent Record**: Stores proof metadata on-chain for auditability
- **Oracle-Only Writes**: Only authorized oracle can register proofs

**Key Functions:**
```solidity
registerProof(bytes32 proofHash, address actor, string actionType, uint256 timestamp)
getProof(bytes32 proofHash) → (address, string, uint256, bool)
isProofRegistered(bytes32 proofHash) → bool
```

### 3. **Oracle.sol** — Multisig Verification Authority

Decentralized verification coordinator using k-of-n threshold signatures:

- **Threshold Signatures**: Requires k valid signatures from n authorized signers
- **Deterministic Verification**: Each signature attests to `Valid(a) ⟺ H(output(a)) = h_chain(a)`
- **Timelock Governance**: 48-hour delay for threshold parameter changes
- **Replay Protection**: Nonce-based request IDs prevent double-execution
- **Coordinated Minting**: Atomically registers proof and mints tokens

**Key Functions:**
```solidity
verifyAndMint(address actor, uint256 amount, bytes32 proofHash, bytes[] signatures) → bytes32
addSigner(address signer)                    // Owner-only
removeSigner(address signer)                 // Owner-only
proposeThresholdUpdate(uint256 newThreshold) // Timelock
```

## Contract Interaction Flow

```
┌─────────────┐
│   Actor     │ Performs useful work
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Verifiers      │ k-of-n signers verify: H(output) = h_chain
│  (off-chain)    │ Sign: (actor, amount, proofHash)
└──────┬──────────┘
       │
       ▼ k signatures
┌─────────────────┐
│   Oracle.sol    │ verifyAndMint(actor, amount, proofHash, sigs)
└──────┬──────────┘
       │
       ├───────────────────────────┐
       │                           │
       ▼                           ▼
┌──────────────┐          ┌──────────────────┐
│ Registry.sol │          │   MikoToken.sol  │
│              │          │                  │
│ registerProof│          │ mint(to, amount, │
│ (actor,type) │          │      proofHash)  │
└──────────────┘          └──────────────────┘
       │                           │
       └───────────┬───────────────┘
                   ▼
           ✅ Tokens minted
           📝 Proof registered
           🔗 Provenance established
```

## Deployment

```javascript
// 1. Deploy ProofRegistry
const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
const registry = await ProofRegistry.deploy(oracleAddress); // Placeholder, update after Oracle deploy

// 2. Deploy MikoToken
const MikoToken = await ethers.getContractFactory("MikoToken");
const token = await MikoToken.deploy(oracleAddress); // Placeholder

// 3. Deploy Oracle with initial signers
const Oracle = await ethers.getContractFactory("Oracle");
const oracle = await Oracle.deploy(
    token.address,
    registry.address,
    [signer1, signer2, signer3], // Initial k signers
    2 // Threshold (k=2)
);

// 4. Update placeholder oracle addresses
await token.updateOracle(oracle.address);
await registry.updateOracle(oracle.address);
```

## Security Considerations

### 1. **Oracle Centralization**
The oracle is a trusted component. Mitigations:
- **Multisig**: Requires k-of-n signatures (e.g., 5-of-9)
- **Transparency**: All verifications logged on-chain via events
- **Upgrade Path**: Owner can rotate signers if compromise detected

### 2. **Proof Hash Collisions**
- Uses SHA-256 (collision-resistant)
- On-chain duplicate rejection in both `MikoToken` and `ProofRegistry`
- Probability of collision: ~2^-256 (negligible)

### 3. **Sybil Resistance**
Economic defense via Section 6 of paper:
```
R(a)·P ≤ C(a)
```
If token price `P` falls, farming becomes unprofitable (cost exceeds reward).

### 4. **Timelock Bypass**
Threshold changes require 48-hour delay, preventing rapid governance attacks.

## Gas Optimization Notes

- `verifyAndMint()` batches proof registration + minting (saves 1 transaction vs separate calls)
- Signature verification uses `ecrecover` (native precompile, ~3000 gas per sig)
- Proof storage uses single `mapping(bytes32 => Proof)` (1 SSTORE per proof)

## Testing

See `../test/test_contracts.js` for:
- ERC-20 compliance tests
- Duplicate proof rejection
- Multisig threshold verification
- Timelock enforcement
- Event emission validation

## License

Apache 2.0 — See [../LICENSE](../LICENSE)
