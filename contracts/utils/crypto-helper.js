const { ethers } = require("hardhat");

/**
 * Signs a climate data report payload using an ethers signer.
 * This matches the exact keccak256 packed ABI encoding format expected by KilimaShieldOracle.
 */
async function signReport(signer, h3IndexBytes32, timestamp, rainfall, ndvi) {
  const payloadHash = ethers.solidityPackedKeccak256(
    ["bytes32", "uint256", "uint256", "uint256"],
    [h3IndexBytes32, timestamp, rainfall, ndvi]
  );
  // signMessage expects a BytesLike or string message
  const signature = await signer.signMessage(ethers.getBytes(payloadHash));
  return signature;
}

module.exports = {
  signReport
};
