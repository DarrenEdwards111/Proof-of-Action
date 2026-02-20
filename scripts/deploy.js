const hre = require("hardhat");

async function main() {
  const [deployer] = await hre.ethers.getSigners();
  console.log("Deploying with:", deployer.address);
  console.log("Balance:", hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address)), "ETH");

  // 1. Deploy ProofRegistry
  console.log("\n1. Deploying ProofRegistry...");
  const ProofRegistry = await hre.ethers.getContractFactory("ProofRegistry");
  const registry = await ProofRegistry.deploy();
  await registry.waitForDeployment();
  const registryAddr = await registry.getAddress();
  console.log("   ProofRegistry:", registryAddr);

  // 2. Deploy MikoToken
  console.log("\n2. Deploying Mikocoin (MikoToken)...");
  const MikoToken = await hre.ethers.getContractFactory("MikoToken");
  const token = await MikoToken.deploy();
  await token.waitForDeployment();
  const tokenAddr = await token.getAddress();
  console.log("   Mikocoin:", tokenAddr);

  // 3. Deploy Oracle (1-of-1 multisig with deployer as signer)
  console.log("\n3. Deploying Oracle...");
  const Oracle = await hre.ethers.getContractFactory("Oracle");
  const oracle = await Oracle.deploy(tokenAddr, registryAddr, [deployer.address], 1);
  await oracle.waitForDeployment();
  const oracleAddr = await oracle.getAddress();
  console.log("   Oracle:", oracleAddr);

  // 4. Set oracle on MikoToken
  console.log("\n4. Setting Oracle as authorized minter...");
  const setOracleTx = await token.setOracle(oracleAddr);
  await setOracleTx.wait();
  console.log("   Oracle set on MikoToken ✓");

  // 5. Set oracle on ProofRegistry
  console.log("\n5. Authorizing Oracle on ProofRegistry...");
  const setRegistryOracleTx = await registry.setOracle(oracleAddr);
  await setRegistryOracleTx.wait();
  console.log("   Oracle authorized on ProofRegistry ✓");

  console.log("\n======================================");
  console.log("DEPLOYMENT COMPLETE - Base Sepolia");
  console.log("======================================");
  console.log("Mikocoin (MIKO):", tokenAddr);
  console.log("ProofRegistry:  ", registryAddr);
  console.log("Oracle:         ", oracleAddr);
  console.log("Deployer/Signer:", deployer.address);
  console.log("======================================");
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
