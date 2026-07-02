const { ethers } = require("hardhat");

async function main() {
  const [deployer] = await ethers.getSigners();
  console.log("Deploying BimaGrid contracts with the account:", deployer.address);

  // 1. Deploy PolicyRegistry
  const PolicyRegistry = await ethers.getContractFactory("PolicyRegistry");
  const policyRegistry = await PolicyRegistry.deploy();
  await policyRegistry.waitForDeployment();
  const policyRegistryAddress = await policyRegistry.getAddress();
  console.log("PolicyRegistry deployed to:", policyRegistryAddress);

  // 2. Deploy EscrowVault
  const EscrowVault = await ethers.getContractFactory("EscrowVault");
  const escrowVault = await EscrowVault.deploy();
  await escrowVault.waitForDeployment();
  const escrowVaultAddress = await escrowVault.getAddress();
  console.log("EscrowVault deployed to:", escrowVaultAddress);

  // 3. Deploy MitigationVerifier
  const MitigationVerifier = await ethers.getContractFactory("MitigationVerifier");
  const mitigationVerifier = await MitigationVerifier.deploy();
  await mitigationVerifier.waitForDeployment();
  const mitigationVerifierAddress = await mitigationVerifier.getAddress();
  console.log("MitigationVerifier deployed to:", mitigationVerifierAddress);

  // 4. Deploy KilimaShieldOracle
  const KilimaShieldOracle = await ethers.getContractFactory("KilimaShieldOracle");
  const oracle = await KilimaShieldOracle.deploy(policyRegistryAddress, escrowVaultAddress);
  await oracle.waitForDeployment();
  const oracleAddress = await oracle.getAddress();
  console.log("KilimaShieldOracle deployed to:", oracleAddress);

  // 5. Transfer ownership of registry and escrow to oracle
  console.log("Configuring registry and escrow ownership...");
  const tx1 = await policyRegistry.transferOwnership(oracleAddress);
  await tx1.wait();
  console.log("PolicyRegistry ownership transferred to KilimaShieldOracle");

  const tx2 = await escrowVault.transferOwnership(oracleAddress);
  await tx2.wait();
  console.log("EscrowVault ownership transferred to KilimaShieldOracle");

  console.log("Deployment and configuration completed successfully!");
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
