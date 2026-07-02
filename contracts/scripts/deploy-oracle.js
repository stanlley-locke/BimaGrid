const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying KilimaShieldOracle with the account:", deployer.address);

  // Addresses would normally be set to your deployed registry/vault addresses
  const policyRegistryAddress = process.env.POLICY_REGISTRY || "0x5FbDB2315678afecb367f032d93F642f64180aa3";
  const escrowVaultAddress = process.env.ESCROW_VAULT || "0xe7f1725E7734CE288F8367e1Bb143E90bb3F0512";

  const KilimaShieldOracle = await ethers.getContractFactory("KilimaShieldOracle");
  const oracle = await KilimaShieldOracle.deploy(policyRegistryAddress, escrowVaultAddress);
  await oracle.waitForDeployment();
  console.log("KilimaShieldOracle deployed to:", await oracle.getAddress());
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
