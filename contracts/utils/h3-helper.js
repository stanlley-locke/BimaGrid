const { ethers } = require("hardhat");

/**
 * Packs an H3 index (64-bit integer hex string) into a bytes32 format.
 * Padding on the left with zeroes to make it 32-bytes.
 * Handles prepended "0x" and uneven character counts.
 */
function packH3Index(h3Str) {
  let clean = h3Str.replace(/^0x/i, "");
  if (clean.length % 2 !== 0) {
    clean = "0" + clean;
  }
  return ethers.zeroPadValue("0x" + clean, 32);
}

module.exports = {
  packH3Index
};
