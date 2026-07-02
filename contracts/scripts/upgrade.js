const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Upgrading oracle module with the account:", deployer.address);

  const policyRegistryAddress = process.env.POLICY_REGISTRY;
  const escrowVaultAddress = process.env.ESCROW_VAULT;
  
  if (!policyRegistryAddress || !escrowVaultAddress) {
    console.error("Please run the script with environment variables set: POLICY_REGISTRY and ESCROW_VAULT");
    process.exit(1);
  }

  // 1. Deploy new version of the Oracle
  const KilimaShieldOracle = await ethers.getContractFactory("KilimaShieldOracle");
  const newOracle = await KilimaShieldOracle.deploy(policyRegistryAddress, escrowVaultAddress);
  await newOracle.waitForDeployment();
  const newOracleAddress = await newOracle.getAddress();
  console.log("New KilimaShieldOracle deployed to:", newOracleAddress);

  // 2. Print upgrade instructions
  console.log("\n==================================================");
  console.log("UPGRADE INSTRUCTIONS:");
  console.log("To complete the upgrade, transfer ownership of your registry and escrow contracts to the new oracle:");
  console.log(`1. Call transferOwnership("${newOracleAddress}") on PolicyRegistry (${policyRegistryAddress})`);
  console.log(`2. Call transferOwnership("${newOracleAddress}") on EscrowVault (${escrowVaultAddress})`);
  console.log("==================================================");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
