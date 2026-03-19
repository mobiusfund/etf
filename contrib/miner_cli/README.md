# HODL ETF Subnet - Miner CLI Tool

A command-line interface for managing TrustedStake index delegations on the HODL ETF Subnet (SN118).

## Overview

This CLI tool provides miners with a simple, interactive way to delegate and undelegate from TrustedStake indexes without using the web interface. It uses Substrate proxy calls to manage delegations directly from the terminal.

## Features

- **List Indexes**: View all available TrustedStake indexes
- **Delegate**: Add an index as a proxy delegate to start mining (auto-enables RealPaysFee)
- **Undelegate**: Remove a proxy delegate to stop mining
- **Status**: Read-only check of proxy and RealPaysFee status (no signing, no wallet unlock)
- **Enable RealPaysFee**: Standalone command to opt-in to RealPaysFee for existing proxies
- **Interactive Mode**: Prompts for missing arguments
- **Network Selection**: Works with finney (mainnet), test, and local networks
- **Version Safety**: Hard-fails on known vulnerable bittensor package versions

## Prerequisites

### 1. Register Your Miner
```bash
btcli subnet register --wallet.name <your_coldkey> --wallet.hotkey <your_hotkey> --netuid 118
```

### 2. Install Dependencies
```bash
cd /path/to/etf
python -m venv venv
source venv/bin/activate
pip install -e .
pip install substrate-interface bittensor-wallet
```

### 3. Requirements
- Python 3.12+ recommended (3.13 also works)
- Bittensor 9.11+
- Minimum 2 TAO balance
- Registered miner on Subnet 118

## Security Note

The CLI will hard-fail if it detects known vulnerable packages:

* `bittensor-wallet==4.0.2`
* `bittensor-cli==9.18.2`

Recommended remediation:

```bash
pip uninstall -y bittensor-cli bittensor-wallet
pip cache purge
pip install --force-reinstall "bittensor-wallet==4.0.1"
pip install --force-reinstall "bittensor-cli==9.18.1"
```

## Usage

### List Available Indexes

```bash
python contrib/miner_cli/miner_cli.py list
```

### Delegate to an Index

Adds the index as a proxy delegate **and automatically enables RealPaysFee**.

```bash
# Interactive mode
python contrib/miner_cli/miner_cli.py delegate

# With arguments (mainnet, default)
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default

# Testnet
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default --network test

# Skip confirmation
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default --yes
```

When delegation succeeds, the CLI automatically submits `Proxy.set_real_pays_fee(delegate, true)` so your wallet pays standard network fees for proxy-managed actions. If the auto-enable fails for any reason, the delegation itself still succeeds and you can enable later with the `enable-real-pays-fee` command.

### Undelegate from an Index

```bash
# Interactive mode
python contrib/miner_cli/miner_cli.py undelegate

# With arguments
python contrib/miner_cli/miner_cli.py undelegate --index 0 --wallet.name default --wallet.hotkey default

# Testnet
python contrib/miner_cli/miner_cli.py undelegate --index 0 --wallet.name default --wallet.hotkey default --network test
```

### Check Proxy & RealPaysFee Status (Read-Only)

Zero signing, zero password prompt, safe to run anytime. Reads only `Proxy.Proxies` and `Proxy.RealPaysFee` from chain.

```bash
# Mainnet (default)
python contrib/miner_cli/miner_cli.py status --wallet.name default --wallet.hotkey default

# Testnet
python contrib/miner_cli/miner_cli.py status --wallet.name default --wallet.hotkey default --network test
```

**Example output:**
```
Wallet : default
Coldkey: 5DPM...
Network: finney

Staking proxies (1):
----------------------------------------------------------------------
  5HgG... [TrustedStake] RealPaysFee -> ENABLED

Done.
```

### Enable RealPaysFee (Existing Proxies)

For users who already have a proxy but haven't opted into RealPaysFee yet:

```bash
# Mainnet (default)
python contrib/miner_cli/miner_cli.py enable-real-pays-fee --wallet.name default --wallet.hotkey default

# Testnet
python contrib/miner_cli/miner_cli.py enable-real-pays-fee --wallet.name default --wallet.hotkey default --network test

# Skip confirmation
python contrib/miner_cli/miner_cli.py enable-real-pays-fee --wallet.name default --wallet.hotkey default --yes
```

The command auto-selects your delegate using the TrustedStake allowlist:
- Exactly one known TrustedStake Staking proxy found -> uses it automatically
- Multiple Staking proxies found -> prompts you to choose from the list
- One unknown Staking proxy -> uses it with a warning

## Command Reference

| Command | Description | Signing Required |
|---------|-------------|-----------------|
| `list` | List available indexes | No |
| `delegate` | Add proxy + auto-enable RealPaysFee | Yes |
| `undelegate` | Remove proxy | Yes |
| `status` | Check proxy & RealPaysFee status | No |
| `enable-real-pays-fee` | Enable RealPaysFee for existing proxy | Yes |

### Common Options

| Option | Description | Default |
|--------|-------------|---------|
| `--wallet.name` | Wallet name (coldkey) | Interactive prompt |
| `--wallet.hotkey` | Wallet hotkey | Interactive prompt |
| `--network` | `finney`, `test`, or `local` | `finney` |
| `--yes`, `-y` | Skip confirmation prompt | Off |
| `--index` | Index number 0-4 (delegate/undelegate only) | Interactive prompt |

## What is RealPaysFee?

`RealPaysFee` is a new opt-in flag on Subtensor's Proxy pallet. When enabled, the **real** (proxied) account pays the standard network transaction fees for actions performed through the proxy, rather than the delegate paying them.

### What it does
- Your wallet pays normal network fees for TrustedStake proxy-managed actions
- One-time on-chain transaction: `Proxy.set_real_pays_fee(delegate, true)`
- If the proxy is removed, the RealPaysFee setting for that pair is automatically cleared

### What it does NOT do
- Does not recreate your proxy
- Does not change custody
- Does not require your mnemonic

## What Happens When You Delegate

1. **Adds Proxy**: The index is added as a "Staking" proxy delegate
2. **Reserve Lock**: ~0.1 TAO is locked as a proxy reserve (refunded on undelegate)
3. **RealPaysFee**: Automatically enabled for the new proxy
4. **Pending Status**: Your position shows "Pending" until the hourly rebalancer runs
5. **Start Earning**: Rewards based on: `score = S * (1 + 0.25 * ln(1 + D/30))`

## What Happens When You Undelegate

1. **Removes Proxy**: The proxy delegate is removed
2. **Reserve Refund**: The ~0.1 TAO proxy reserve is automatically refunded
3. **RealPaysFee Cleared**: Automatically cleared when proxy is removed
4. **Manual Unstaking**: You may need to manually unstake via `btcli st remove`

## Testnet Workflow

To test the full delegate + RealPaysFee flow on testnet:

```bash
# 1. Delegate on testnet
python contrib/miner_cli/miner_cli.py delegate \
    --index 0 --wallet.name test-wallet --wallet.hotkey default --network test --yes

# 2. Check status on testnet
python contrib/miner_cli/miner_cli.py status \
    --wallet.name test-wallet --wallet.hotkey default --network test

# 3. Undelegate on testnet
python contrib/miner_cli/miner_cli.py undelegate \
    --index 0 --wallet.name test-wallet --wallet.hotkey default --network test --yes
```

## Supported Indexes

| Index | Name | Description |
|-------|------|-------------|
| 0 | TSBCSI | Broad market index |
| 1 | Top 10 | Top performing subnets |
| 2 | Full Stack | Diversified portfolio |
| 3 | Fintech | Financial subnets |
| 4 | Bittensor Universe | Comprehensive coverage |

## Testing

```bash
# Install test dependencies
pip install -r contrib/miner_cli/requirements-test.txt

# Run all tests
cd contrib/miner_cli
pytest test_miner_cli.py test_proxy_utils.py -v

# Run with coverage
pytest test_miner_cli.py test_proxy_utils.py --cov=. --cov-report=html
```

## File Structure

```
contrib/miner_cli/
├── miner_cli.py          # Main CLI entry point
├── proxy_utils.py         # Shared chain query & RealPaysFee utilities
├── test_miner_cli.py      # Tests for CLI commands
├── test_proxy_utils.py    # Tests for proxy utilities
├── README.md
├── pytest.ini
└── requirements-test.txt
```

## Support & Resources

- **Subnet FAQ**: [/Docs/FAQ.md](../../Docs/FAQ.md)
- **TrustedStake Docs**: https://trustedstake.gitbook.io/trustedstake/
- **TrustedStake App**: https://app.trustedstake.ai/strat
- **Bittensor Docs**: https://docs.learnbittensor.org/
