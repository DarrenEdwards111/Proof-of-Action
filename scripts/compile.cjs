const solc = require('solc');
const fs = require('fs');
const path = require('path');

const contractsDir = path.join(__dirname, '..', 'contracts');

const input = {
  language: 'Solidity',
  sources: {
    'interfaces/IProofOfAction.sol': { content: fs.readFileSync(path.join(contractsDir, 'interfaces', 'IProofOfAction.sol'), 'utf8') },
    'MikoToken.sol': { content: fs.readFileSync(path.join(contractsDir, 'MikoToken.sol'), 'utf8') },
    'ProofRegistry.sol': { content: fs.readFileSync(path.join(contractsDir, 'ProofRegistry.sol'), 'utf8') },
    'Oracle.sol': { content: fs.readFileSync(path.join(contractsDir, 'Oracle.sol'), 'utf8') }
  },
  settings: {
    outputSelection: { '*': { '*': ['abi', 'evm.bytecode.object'] } },
    optimizer: { enabled: true, runs: 200 }
  }
};

const output = JSON.parse(solc.compile(JSON.stringify(input)));

if (output.errors) {
  const fatal = output.errors.filter(e => e.severity === 'error');
  if (fatal.length > 0) {
    console.error(JSON.stringify(fatal, null, 2));
    process.exit(1);
  }
  output.errors.filter(e => e.severity === 'warning').forEach(w => console.error('Warning:', w.message));
}

fs.writeFileSync(path.join(__dirname, '..', 'compiled.json'), JSON.stringify(output.contracts, null, 2));
console.log('Compilation successful');
