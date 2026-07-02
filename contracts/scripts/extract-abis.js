const fs = require('fs');
const path = require('path');

const contracts = [
  'KilimaShieldOracle',
  'PolicyRegistry',
  'EscrowVault',
  'MitigationVerifier',
  'PolicyNFT',
  'BimaToken'
];

const artifactsDir = path.join(__dirname, '../artifacts/contracts');
const abiDir = path.join(__dirname, '../abi');

if (!fs.existsSync(abiDir)) {
  fs.mkdirSync(abiDir, { recursive: true });
}

contracts.forEach(contractName => {
  let artifactPath = '';
  const searchDirs = ['core', 'tokens', 'mocks'];
  
  for (const sDir of searchDirs) {
    const filePath = path.join(artifactsDir, sDir, `${contractName}.sol`, `${contractName}.json`);
    if (fs.existsSync(filePath)) {
      artifactPath = filePath;
      break;
    }
  }
  
  if (!artifactPath) {
    console.error(`Artifact not found for ${contractName}`);
    return;
  }
  
  const artifact = JSON.parse(fs.readFileSync(artifactPath, 'utf8'));
  const abiFile = path.join(abiDir, `${contractName}.json`);
  fs.writeFileSync(abiFile, JSON.stringify(artifact.abi, null, 2));
  console.log(`Extracted ABI for ${contractName} -> abi/${contractName}.json`);
});
