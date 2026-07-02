const hre = require("hardhat");

async function main() {
  const policyRegistryAddress = process.env.POLICY_REGISTRY;
  const escrowVaultAddress = process.env.ESCROW_VAULT;
  const oracleAddress = process.env.ORACLE;

  if (!policyRegistryAddress || !escrowVaultAddress || !oracleAddress) {
    console.error("Please run the script with environment variables set: POLICY_REGISTRY, ESCROW_VAULT, and ORACLE");
    process.exit(1);
  }

  console.log("Verifying PolicyRegistry...");
  try {
    await hre.run("verify:verify", {
      address: policyRegistryAddress,
      constructorArguments: [],
    });
  } catch (error) {
    console.error("PolicyRegistry verification failed:", error.message);
  }

  console.log("Verifying EscrowVault...");
  try {
    await hre.run("verify:verify", {
      address: escrowVaultAddress,
      constructorArguments: [],
    });
  } catch (error) {
    console.error("EscrowVault verification failed:", error.message);
  }

  console.log("Verifying KilimaShieldOracle...");
  try {
    await hre.run("verify:verify", {
      address: oracleAddress,
      constructorArguments: [policyRegistryAddress, escrowVaultAddress],
    });
  } catch (error) {
    console.error("KilimaShieldOracle verification failed:", error.message);
  }
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
