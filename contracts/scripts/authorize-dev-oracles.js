const { ethers } = require("hardhat");

const KILIMA_ORACLE = process.env.CONTRACT_KILIMA_SHIELD_ORACLE || "0x5FbDB2315678afecb367f032d93F642f64180aa3";

const DEV_ORACLE_SIGNERS = [
	"0x70997970C51812dc3A010C7d01b50e0d17dc79C8",
	"0x3C44CdDdB6a900fa2b585dd299e03d12FA4293BC",
	"0x90F79bf6EB2c4f870365E785982E1f101E93b906",
];

async function main() {
	const [deployer] = await ethers.getSigners();
	console.log("Configuring oracles with deployer:", deployer.address);

	const oracle = await ethers.getContractAt("KilimaShieldOracle", KILIMA_ORACLE);

	for (const addr of DEV_ORACLE_SIGNERS) {
		const tx = await oracle.setAuthorizedOracle(addr, true);
		await tx.wait();
		console.log("Authorized:", addr);
	}
}

main()
	.then(() => process.exit(0))
	.catch((error) => {
		console.error(error);
		process.exit(1);
	});
