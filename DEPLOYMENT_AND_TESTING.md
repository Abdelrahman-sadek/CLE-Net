# CLE-Net Deployment and Testing Guide

This guide provides step-by-step instructions for deploying and testing CLE-Net.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Testing](#testing)
- [Testnet Deployment](#testnet-deployment)
- [Mainnet Deployment](#mainnet-deployment)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

---

## Prerequisites

Before deploying or testing CLE-Net, ensure you have the following:

### System Requirements

- **Operating System**: Linux, macOS, or Windows (with WSL2)
- **Python**: 3.8 or higher
- **Memory**: 4GB RAM minimum (8GB recommended)
- **Disk Space**: 10GB free space
- **Network**: Stable internet connection for P2P networking

### Software Dependencies

```bash
# Python 3.8+
python --version

# pip (Python package manager)
pip --version

# Git (for cloning the repository)
git --version
```

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Abdelrahman-sadek/CLE-Net.git
cd CLE-Net
```

### 2. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import core; print('CLE-Net installed successfully!')"
```

### 3. Verify Installation

```bash
# Run a quick verification
python -c "
from core.cosmos.app.app import CLENetApp, AppConfig
from core.cosmos.tendermint import TendermintBFT
from core.cosmos.state_machine import CognitiveStateMachine
print('All modules imported successfully!')
"
```

---

## Testing

CLE-Net includes a comprehensive test suite to ensure all components work correctly.

### Running All Tests

```bash
# Run all tests (unit + integration)
python scripts/run_tests.py
```

### Running Unit Tests Only

```bash
# Run only unit tests
python scripts/run_tests.py --unit
```

### Running Integration Tests Only

```bash
# Run only integration tests
python scripts/run_tests.py --integration
```

### Running Specific Test Files

```bash
# Run state machine tests
python -m unittest tests.test_state_machine

# Run Tendermint BFT tests
python -m unittest tests.test_tendermint

# Run Cosmos SDK app tests
python -m unittest tests.test_cosmos_app

# Run integration tests
python -m unittest tests.test_integration
```

### Test Coverage

The test suite covers:

- **State Machine Tests** ([`tests/test_state_machine.py`](tests/test_state_machine.py))
  - Law state transitions (valid and invalid)
  - CCS state transitions
  - Validator state transitions
  - Block commitment
  - Transition history tracking
  - State validation
  - State export/import

- **Tendermint BFT Tests** ([`tests/test_tendermint.py`](tests/test_tendermint.py))
  - Initialization and configuration
  - Validator management
  - Proposer rotation
  - Block proposal
  - Voting mechanism
  - Consensus checking
  - Block commitment
  - Block retrieval
  - State validation

- **Cosmos SDK App Tests** ([`tests/test_cosmos_app.py`](tests/test_cosmos_app.py))
  - App initialization
  - Module registration/unregistration
  - Chain initialization
  - Block lifecycle
  - Query handling
  - State management

- **Integration Tests** ([`tests/test_integration.py`](tests/test_integration.py))
  - App-Tendermint integration
  - App-state machine integration
  - Tendermint-state machine integration
  - Full integration workflow
  - Law proposal workflow
  - Multiple blocks workflow

### Expected Test Results

All tests should pass with output similar to:

```
test_initialization (tests.test_state_machine.TestCognitiveStateMachine) ... ok
test_law_state_transitions (tests.test_state_machine.TestCognitiveStateMachine) ... ok
test_invalid_law_transitions (tests.test_state_machine.TestCognitiveStateMachine) ... ok
...
----------------------------------------------------------------------
Ran 50 tests in 2.345s

OK
```

---

## Testnet Deployment

Deploying a testnet allows you to test CLE-Net in a controlled environment before going to mainnet.

### Step 1: Configure Testnet

The testnet configuration is automatically created when you run the deployment script. You can customize it by editing [`config/testnet.toml`](config/testnet.toml):

```json
{
  "chain_id": "clenet-testnet-1",
  "genesis_time": "2026-02-10T00:00:00.000Z",
  "initial_height": 1,
  "block_time": 5.0,
  "validators": [
    {
      "address": "validator1",
      "stake": 1000000,
      "role": "cognitive_miner"
    },
    {
      "address": "validator2",
      "stake": 1000000,
      "role": "state_validator"
    },
    {
      "address": "validator3",
      "stake": 1000000,
      "role": "conflict_resolver"
    },
    {
      "address": "validator4",
      "stake": 1000000,
      "role": "watchdog"
    }
  ],
  "accounts": [
    {
      "address": "user1",
      "balance": 1000000
    },
    {
      "address": "user2",
      "balance": 1000000
    }
  ]
}
```

### Step 2: Deploy Testnet

```bash
# Deploy testnet
python scripts/deploy_testnet.py
```

This will:
1. Create the genesis file at [`data/testnet/genesis.json`](data/testnet/genesis.json)
2. Initialize the CLE-Net application
3. Set up Tendermint BFT
4. Initialize the cognitive state machine
5. Display a deployment summary

Expected output:

```
============================================================
CLE-Net Testnet Deployment
============================================================

[1/4] Initializing CLE-Net application...
✓ Application initialized

[2/4] Initializing Tendermint BFT...
✓ Tendermint BFT initialized

[3/4] Initializing cognitive state machine...
✓ State machine initialized

[4/4] Saving genesis file...
✓ Genesis file saved to data/testnet/genesis.json

============================================================
Deployment Summary
============================================================
Chain ID: clenet-testnet-1
Initial Height: 1
Block Time: 5.0s
Validators: 4
Accounts: 2
Genesis File: data/testnet/genesis.json
============================================================

✓ Testnet deployed successfully!

To start the testnet, run:
  python scripts/start_testnet.py
```

### Step 3: Start Testnet Node

```bash
# Start testnet node
python scripts/start_testnet.py
```

This will:
1. Load the genesis file
2. Initialize the application
3. Start Tendermint BFT
4. Begin producing blocks

Expected output:

```
Initializing testnet node...
✓ Testnet node initialized

Starting testnet node...
Proposed block 1 by validator1
Committed block 1
Proposed block 2 by validator2
Committed block 2
...
```

### Step 4: Check Node Status

```bash
# Check node status
python scripts/start_testnet.py --status
```

Expected output:

```
============================================================
Testnet Node Status
============================================================
Running: True
Chain ID: clenet-testnet-1
Block Height: 10
Last Block Hash: abc123...
Validators: 4
============================================================
```

### Step 5: Stop Testnet Node

Press `Ctrl+C` to stop the testnet node gracefully.

---

## Mainnet Deployment

Deploying to mainnet requires careful preparation and security considerations.

### Step 1: Configure Mainnet

The mainnet configuration is automatically created when you run the deployment script. You can customize it by editing [`config/mainnet.toml`](config/mainnet.toml):

```json
{
  "chain_id": "clenet-mainnet-1",
  "genesis_time": "2026-02-10T00:00:00.000Z",
  "initial_height": 1,
  "block_time": 6.0,
  "validators": [
    {
      "address": "validator1",
      "stake": 10000000,
      "role": "cognitive_miner"
    },
    {
      "address": "validator2",
      "stake": 10000000,
      "role": "state_validator"
    },
    {
      "address": "validator3",
      "stake": 10000000,
      "role": "conflict_resolver"
    },
    {
      "address": "validator4",
      "stake": 10000000,
      "role": "watchdog"
    }
  ],
  "accounts": [
    {
      "address": "treasury",
      "balance": 100000000
    },
    {
      "address": "community_pool",
      "balance": 50000000
    }
  ],
  "security": {
    "min_stake": 1000000,
    "max_validators": 100,
    "slash_fraction_double_sign": "0.050000000000000000",
    "slash_fraction_downtime": "0.010000000000000000",
    "min_signed_per_window": "0.500000000000000000",
    "signed_blocks_window": 100
  }
}
```

### Step 2: Deploy Mainnet

```bash
# Deploy mainnet
python scripts/deploy_mainnet.py
```

This will:
1. Validate security configuration
2. Create the genesis file at [`data/mainnet/genesis.json`](data/mainnet/genesis.json)
3. Initialize the CLE-Net application
4. Set up Tendermint BFT
5. Initialize the cognitive state machine
6. Save configuration at [`data/mainnet/config.json`](data/mainnet/config.json)
7. Display a deployment summary with security notes

Expected output:

```
============================================================
CLE-Net Mainnet Deployment
============================================================

[0/5] Validating security configuration...
✓ Security configuration validated

[1/5] Initializing CLE-Net application...
✓ Application initialized

[2/5] Initializing Tendermint BFT...
✓ Tendermint BFT initialized

[3/5] Initializing cognitive state machine...
✓ State machine initialized

[4/5] Saving genesis file...
✓ Genesis file saved to data/mainnet/genesis.json

[5/5] Saving configuration...
✓ Configuration saved to data/mainnet/config.json

============================================================
Deployment Summary
============================================================
Chain ID: clenet-mainnet-1
Initial Height: 1
Block Time: 6.0s
Validators: 4
Accounts: 2
Genesis File: data/mainnet/genesis.json
Configuration: data/mainnet/config.json
============================================================

============================================================
Security Configuration
============================================================
Minimum Stake: 1000000 uCLE
Max Validators: 100
Slash Fraction (Double Sign): 0.05
Slash Fraction (Downtime): 0.01
Min Signed Per Window: 0.5
Signed Blocks Window: 100
============================================================

✓ Mainnet deployed successfully!

⚠️  IMPORTANT SECURITY NOTES:
  1. Review and update validator addresses
  2. Ensure all validators have proper key management
  3. Test thoroughly before going live
  4. Have a rollback plan ready
  5. Monitor the network closely after launch

To start the mainnet, run:
  python scripts/start_mainnet.py
```

### Step 3: Start Mainnet Node

```bash
# Start mainnet node
python scripts/start_mainnet.py
```

### Step 4: Check Node Status

```bash
# Check node status
python scripts/start_mainnet.py --status
```

### Step 5: Stop Mainnet Node

Press `Ctrl+C` to stop the mainnet node gracefully.

---

## Troubleshooting

### Common Issues

#### Issue: Tests Fail to Run

**Symptom**: `ModuleNotFoundError: No module named 'core'`

**Solution**:
```bash
# Ensure you're in the project root directory
cd CLE-Net

# Reinstall dependencies
pip install -r requirements.txt
```

#### Issue: Testnet Deployment Fails

**Symptom**: `FileNotFoundError: Configuration file not found`

**Solution**:
```bash
# Create config directory if it doesn't exist
mkdir -p config

# Run deployment again
python scripts/deploy_testnet.py
```

#### Issue: Node Won't Start

**Symptom**: `FileNotFoundError: Genesis file not found`

**Solution**:
```bash
# Ensure genesis file exists
ls data/testnet/genesis.json

# If not found, redeploy
python scripts/deploy_testnet.py
```

#### Issue: Port Already in Use

**Symptom**: `OSError: [Errno 48] Address already in use`

**Solution**:
```bash
# Find and kill the process using the port
# On Linux/macOS:
lsof -i :26657 | grep LISTEN
kill -9 <PID>

# On Windows:
netstat -ano | findstr :26657
taskkill /PID <PID> /F
```

#### Issue: Tests Timeout

**Symptom**: Tests hang or timeout

**Solution**:
```bash
# Run tests with increased timeout
python -m unittest tests.test_integration -v --timeout=60
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/Abdelrahman-sadek/CLE-Net/issues)
2. Review the [Documentation](docs/)
3. Ask for help in the [Discussions](https://github.com/Abdelrahman-sadek/CLE-Net/discussions)

---

## Best Practices

### Testing Best Practices

1. **Run Tests Before Deployment**
   ```bash
   # Always run tests before deploying
   python scripts/run_tests.py
   ```

2. **Run Tests After Changes**
   ```bash
   # Run tests after making changes
   python scripts/run_tests.py
   ```

3. **Use Specific Test Suites**
   ```bash
   # Run only unit tests for quick feedback
   python scripts/run_tests.py --unit
   ```

### Deployment Best Practices

1. **Test on Testnet First**
   ```bash
   # Always test on testnet before mainnet
   python scripts/deploy_testnet.py
   python scripts/start_testnet.py
   ```

2. **Backup Configuration**
   ```bash
   # Backup your configuration before deployment
   cp config/mainnet.toml config/mainnet.toml.backup
   ```

3. **Monitor Node Health**
   ```bash
   # Regularly check node status
   python scripts/start_mainnet.py --status
   ```

4. **Keep Software Updated**
   ```bash
   # Update dependencies regularly
   pip install --upgrade -r requirements.txt
   ```

### Security Best Practices

1. **Use Strong Validator Addresses**
   - Generate cryptographically secure validator addresses
   - Never share private keys
   - Use hardware wallets for mainnet validators

2. **Review Security Configuration**
   - Check [`config/mainnet.toml`](config/mainnet.toml) security settings
   - Ensure minimum stake is appropriate
   - Verify slash fractions are set correctly

3. **Monitor Network Activity**
   - Watch for unusual validator behavior
   - Monitor block production rates
   - Track consensus participation

4. **Have a Rollback Plan**
   - Keep backups of genesis files
   - Document rollback procedures
   - Test rollback procedures on testnet

---

## Next Steps

After successfully deploying and testing CLE-Net:

1. **Explore the Codebase**
   - Read the [Architecture Documentation](docs/architecture/)
   - Review the [Whitepaper](docs/whitepaper/05_complete_whitepaper.md)

2. **Contribute**
   - Check the [Contributing Guidelines](CONTRIBUTING.md)
   - Review [Open Issues](https://github.com/Abdelrahman-sadek/CLE-Net/issues)

3. **Build on CLE-Net**
   - Develop custom modules
   - Integrate with other blockchains
   - Build applications on top of CLE-Net

---

## Additional Resources

- [README.md](README.md) - Project overview
- [ROADMAP.md](ROADMAP.md) - Development roadmap
- [Documentation](docs/) - Detailed documentation
- [Examples](examples/) - Code examples

---

*Last Updated: 2026-02-10*
