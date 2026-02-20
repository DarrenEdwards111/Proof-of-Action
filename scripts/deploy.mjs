import { readFileSync } from "fs";
import { execSync } from "child_process";
import { ethers } from "ethers";
import path from "path";
import { fileURLToPath } from "url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

async function main() {
  // Compile
  console.log("Compiling contracts...");
  execSync("node scripts/compile.cjs", { cwd: path.join(__dirname, ".."), stdio: "inherit" });
  
  const compiled = JSON.parse(readFileSync(path.join(__dirname, "..", "compiled.json"), "utf8"));
  console.log("Compilation successful ✓\n");

  const PRIVATE_KEY = "a9d486d0576c72ec2c75e49ba00a7d0513982be6e0c356b148db1ea45109a2e8";
  const provider = new ethers.JsonRpcProvider("https://sepolia.base.org");
  const wallet = new ethers.Wallet(PRIVATE_KEY, provider);
  
  console.log("Deployer:", wallet.address);
  const balance = await provider.getBalance(wallet.address);
  console.log("Balance:", ethers.formatEther(balance), "ETH on Base Sepolia\n");

  async function deploy(name, sourceFile, constructorArgs = []) {
    const contract = compiled[sourceFile][name];
    const bytecode = "0x" + contract.evm.bytecode.object;
    console.log(`Deploying ${name}...`);
    const factory = new ethers.ContractFactory(contract.abi, bytecode, wallet);
    const deployed = await factory.deploy(...constructorArgs);
    await deployed.waitForDeployment();
    const addr = await deployed.getAddress();
    console.log(`  ${name}: ${addr}`);
    return { contract: deployed, address: addr, abi: contract.abi };
  }

  // Deploy with temporary oracle (deployer), then update
  const registry = await deploy("ProofRegistry", "ProofRegistry.sol", [wallet.address]);
  const token = await deploy("MikoToken", "MikoToken.sol", [wallet.address]);
  const oracle = await deploy("Oracle", "Oracle.sol", [token.address, registry.address, [wallet.address], 1]);

  // Update oracle references
  console.log("\nSetting Oracle as authorized minter...");
  const tokenContract = new ethers.Contract(token.address, token.abi, wallet);
  const tx1 = await tokenContract.updateOracle(oracle.address);
  await tx1.wait();
  console.log("  Oracle set on MikoToken ✓");

  console.log("Authorizing Oracle on ProofRegistry...");
  const registryContract = new ethers.Contract(registry.address, registry.abi, wallet);
  const tx2 = await registryContract.updateOracle(oracle.address);
  await tx2.wait();
  console.log("  Oracle authorized on ProofRegistry ✓");

  const finalBalance = await provider.getBalance(wallet.address);

  console.log("\n======================================");
  console.log("🚀 DEPLOYMENT COMPLETE - Base Sepolia");
  console.log("======================================");
  console.log(`Mikocoin (MIKO):  ${token.address}`);
  console.log(`ProofRegistry:    ${registry.address}`);
  console.log(`Oracle:           ${oracle.address}`);
  console.log(`Deployer/Signer:  ${wallet.address}`);
  console.log(`Chain:            Base Sepolia (84532)`);
  console.log(`Gas used:         ${ethers.formatEther(balance - finalBalance)} ETH`);
  console.log(`Explorer:         https://sepolia.basescan.org/address/${token.address}`);
  console.log("======================================");
}

main().catch(console.error);
