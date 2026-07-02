import { HardhatUserConfig } from "hardhat/config";
import "@nomicfoundation/hardhat-toolbox";

const config: HardhatUserConfig = {
  solidity: {
    version: "0.8.20",
    settings: {
      optimizer: {
        enabled: true,
        runs: 200
      },
      viaIR: true
    }
  },
  typechain: {
    outDir: "typechain",
    target: "ethers-v6"
  },
  gasReporter: {
    enabled: true,
    outputFile: "gas-report/gas-report.txt",
    noColors: true
  }
};

export default config;
