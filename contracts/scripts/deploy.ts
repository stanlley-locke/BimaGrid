import { ethers } from "hardhat";

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying contracts with the account:", deployer.address);

  const PolicyRegistry = await ethers.getContractFactory("PolicyRegistry");
  const registry = await PolicyRegistry.deploy();
  await registry.waitForDeployment();
  console.log("PolicyRegistry deployed to:", await registry.getAddress());

  const EscrowVault = await ethers.getContractFactory("EscrowVault");
  const escrow = await EscrowVault.deploy();
  await escrow.waitForDeployment();
  console.log("EscrowVault deployed to:", await escrow.getAddress());

  const KilimaShieldOracle = await ethers.getContractFactory("KilimaShieldOracle");
  const oracle = await KilimaShieldOracle.deploy(await registry.getAddress(), await escrow.getAddress());
  await oracle.waitForDeployment();
  console.log("KilimaShieldOracle deployed to:", await oracle.getAddress());
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
