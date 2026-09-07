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
  const oracleAddress = await oracle.getAddress();
  console.log("KilimaShieldOracle deployed to:", oracleAddress);

  await (await registry.transferOwnership(oracleAddress)).wait();
  await (await escrow.transferOwnership(oracleAddress)).wait();

  const devOracleAddresses = [
    "0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
    "0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
    "0x90F79bf6EB2c4f870365E785982E1f101E93b906",
  ];
  for (const addr of devOracleAddresses) {
    await (await oracle.setAuthorizedOracle(addr, true)).wait();
    console.log("Authorized oracle signer:", addr);
  }

  await (await registry.setAuthorizedCaller(oracleAddress, true)).wait();
  await (await escrow.setAuthorizedCaller(oracleAddress, true)).wait();
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
