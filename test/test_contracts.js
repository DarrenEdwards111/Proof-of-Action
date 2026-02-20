/**
 * Proof-of-Action Contract Tests
 * 
 * NOTE: These are pseudo-tests demonstrating expected behavior.
 * For production, use Hardhat/Foundry with actual on-chain deployment.
 */

const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Proof-of-Action Reference Implementation", function () {
  let token, registry, oracle;
  let owner, signer1, signer2, signer3, actor;

  beforeEach(async function () {
    [owner, signer1, signer2, signer3, actor] = await ethers.getSigners();

    // Deploy contracts
    const ProofRegistry = await ethers.getContractFactory("ProofRegistry");
    registry = await ProofRegistry.deploy(owner.address); // Temporary oracle

    const MikoToken = await ethers.getContractFactory("MikoToken");
    token = await MikoToken.deploy(owner.address); // Temporary oracle

    const Oracle = await ethers.getContractFactory("Oracle");
    oracle = await Oracle.deploy(
      token.address,
      registry.address,
      [signer1.address, signer2.address, signer3.address],
      2 // k=2 threshold
    );

    // Update oracle references
    await token.updateOracle(oracle.address);
    await registry.updateOracle(oracle.address);
  });

  describe("MikoToken", function () {
    it("Should mint tokens with valid proof hash", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("action-output-1"));
      const amount = ethers.utils.parseEther("100");

      await expect(token.connect(oracle).mint(actor.address, amount, proofHash))
        .to.emit(token, "Mint")
        .withArgs(actor.address, amount, proofHash);

      expect(await token.balanceOf(actor.address)).to.equal(amount);
      expect(await token.isProofUsed(proofHash)).to.be.true;
    });

    it("Should reject duplicate proof hash", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("action-output-2"));
      const amount = ethers.utils.parseEther("50");

      await token.connect(oracle).mint(actor.address, amount, proofHash);

      await expect(
        token.connect(oracle).mint(actor.address, amount, proofHash)
      ).to.be.revertedWith("MikoToken: proof already used");
    });

    it("Should only allow oracle to mint", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("action-output-3"));
      const amount = ethers.utils.parseEther("100");

      await expect(
        token.connect(actor).mint(actor.address, amount, proofHash)
      ).to.be.revertedWith("MikoToken: caller is not oracle");
    });

    it("Should allow users to burn tokens", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("action-output-4"));
      const amount = ethers.utils.parseEther("100");

      await token.connect(oracle).mint(actor.address, amount, proofHash);
      
      const burnAmount = ethers.utils.parseEther("30");
      await expect(token.connect(actor).burn(burnAmount))
        .to.emit(token, "Burn")
        .withArgs(actor.address, burnAmount);

      expect(await token.balanceOf(actor.address)).to.equal(
        amount.sub(burnAmount)
      );
    });

    it("Should implement ERC-20 transfer", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("action-output-5"));
      const amount = ethers.utils.parseEther("100");

      await token.connect(oracle).mint(actor.address, amount, proofHash);
      
      const transferAmount = ethers.utils.parseEther("25");
      await token.connect(actor).transfer(signer1.address, transferAmount);

      expect(await token.balanceOf(signer1.address)).to.equal(transferAmount);
    });
  });

  describe("ProofRegistry", function () {
    it("Should register proof with metadata", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("verified-action-1"));
      const actionType = "compute-task";
      const timestamp = Math.floor(Date.now() / 1000);

      await expect(
        registry.connect(oracle).registerProof(proofHash, actor.address, actionType, timestamp)
      )
        .to.emit(registry, "ProofRegistered")
        .withArgs(proofHash, actor.address, actionType, timestamp);

      const proof = await registry.getProof(proofHash);
      expect(proof.actor).to.equal(actor.address);
      expect(proof.actionType).to.equal(actionType);
      expect(proof.exists).to.be.true;
    });

    it("Should reject duplicate proof registration", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("verified-action-2"));
      const timestamp = Math.floor(Date.now() / 1000);

      await registry.connect(oracle).registerProof(proofHash, actor.address, "task", timestamp);

      await expect(
        registry.connect(oracle).registerProof(proofHash, actor.address, "task", timestamp)
      ).to.be.revertedWith("ProofRegistry: proof already registered");
    });
  });

  describe("Oracle", function () {
    it("Should verify and mint with threshold signatures", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("multisig-action-1"));
      const amount = ethers.utils.parseEther("200");

      // Create message hash
      const messageHash = ethers.utils.solidityKeccak256(
        ["address", "uint256", "bytes32"],
        [actor.address, amount, proofHash]
      );

      // Sign with k=2 signers
      const sig1 = await signer1.signMessage(ethers.utils.arrayify(messageHash));
      const sig2 = await signer2.signMessage(ethers.utils.arrayify(messageHash));

      await expect(
        oracle.connect(owner).verifyAndMint(actor.address, amount, proofHash, [sig1, sig2])
      )
        .to.emit(oracle, "MintExecuted")
        .and.to.emit(token, "Mint");

      expect(await token.balanceOf(actor.address)).to.equal(amount);
    });

    it("Should reject insufficient signatures", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("insufficient-sigs"));
      const amount = ethers.utils.parseEther("100");

      const messageHash = ethers.utils.solidityKeccak256(
        ["address", "uint256", "bytes32"],
        [actor.address, amount, proofHash]
      );

      const sig1 = await signer1.signMessage(ethers.utils.arrayify(messageHash));

      await expect(
        oracle.connect(owner).verifyAndMint(actor.address, amount, proofHash, [sig1])
      ).to.be.revertedWith("Oracle: insufficient signatures");
    });

    it("Should add and remove signers", async function () {
      const newSigner = ethers.Wallet.createRandom();

      await oracle.connect(owner).addSigner(newSigner.address);
      expect(await oracle.isSigner(newSigner.address)).to.be.true;

      await oracle.connect(owner).removeSigner(newSigner.address);
      expect(await oracle.isSigner(newSigner.address)).to.be.false;
    });

    it("Should enforce timelock on threshold updates", async function () {
      await oracle.connect(owner).proposeThresholdUpdate(3);

      // Should fail before timelock expires
      await expect(
        oracle.connect(owner).executeThresholdUpdate()
      ).to.be.revertedWith("Oracle: timelock not expired");

      // Fast-forward 48 hours (in real test, use Hardhat time manipulation)
      // await ethers.provider.send("evm_increaseTime", [48 * 3600]);
      // await oracle.connect(owner).executeThresholdUpdate();
      // expect(await oracle.getThreshold()).to.equal(3);
    });
  });

  describe("Integration", function () {
    it("Should complete full verification flow", async function () {
      const proofHash = ethers.utils.keccak256(ethers.utils.toUtf8Bytes("full-flow-action"));
      const amount = ethers.utils.parseEther("500");

      const messageHash = ethers.utils.solidityKeccak256(
        ["address", "uint256", "bytes32"],
        [actor.address, amount, proofHash]
      );

      const sig1 = await signer1.signMessage(ethers.utils.arrayify(messageHash));
      const sig2 = await signer2.signMessage(ethers.utils.arrayify(messageHash));

      // Execute full flow
      await oracle.connect(owner).verifyAndMint(actor.address, amount, proofHash, [sig1, sig2]);

      // Verify outcomes
      expect(await token.balanceOf(actor.address)).to.equal(amount);
      expect(await token.isProofUsed(proofHash)).to.be.true;
      expect(await registry.isProofRegistered(proofHash)).to.be.true;

      const proof = await registry.getProof(proofHash);
      expect(proof.actor).to.equal(actor.address);
      expect(proof.exists).to.be.true;
    });
  });
});

/**
 * To run these tests:
 * 
 * 1. Install Hardhat:
 *    npm install --save-dev hardhat @nomiclabs/hardhat-ethers ethers chai
 * 
 * 2. Initialize Hardhat:
 *    npx hardhat
 * 
 * 3. Copy contracts to contracts/ directory
 * 
 * 4. Run tests:
 *    npx hardhat test test/test_contracts.js
 * 
 * Expected behavior summary:
 * - ✅ Tokens mint only with unique proof hashes
 * - ✅ Oracle requires k-of-n threshold signatures
 * - ✅ Proof registry stores immutable action records
 * - ✅ Duplicate proofs rejected across all contracts
 * - ✅ Timelock enforced for governance changes
 * - ✅ Complete provenance: token → proof → actor
 */
