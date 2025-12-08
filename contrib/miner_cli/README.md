# HODL ETF Subnet - Miner CLI Tool

A command-line interface for managing TrustedStake index delegations on the HODL ETF Subnet (SN118).

## Overview

This CLI tool provides miners with a simple, interactive way to delegate and undelegate from TrustedStake indexes without using the web interface. It uses Substrate proxy calls to manage delegations directly from the terminal.

## Features

- ✅ **Interactive Mode**: Prompts for missing arguments, perfect for beginners
- ✅ **List Indexes**: View all available TrustedStake indexes
- ✅ **Delegate**: Add an index as a proxy delegate to start mining
- ✅ **Undelegate**: Remove a proxy delegate to stop mining
- ✅ **Flexible Usage**: Supports both interactive and argument-based modes
- ✅ **Network Selection**: Works with finney, test, and local networks
- ✅ **Safe**: Confirmation prompts for all operations
- ✅ **Non-Custodial**: Uses Substrate proxy mechanism

## Prerequisites

### 1. Register Your Miner
```bash
btcli subnet register --wallet.name <your_coldkey> --wallet.hotkey <your_hotkey> --netuid 118
```

### 2. Install Dependencies
```bash
cd /path/to/etf
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 3. Requirements
- Python 3.8+
- Bittensor 9.11+
- Minimum 2 TAO balance
- Registered miner on Subnet 118

## Installation

The CLI is located in `contrib/miner_cli/miner_cli.py`. No additional installation is needed beyond the subnet dependencies.

## Usage

### List Available Indexes

View all supported TrustedStake indexes:

```bash
python contrib/miner_cli/miner_cli.py list
```

**Output:**
```
============================================================
Available TrustedStake Indexes
============================================================

Index 0: TSBCSI
Address: 5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr

Index 1: Top 10
Address: 5CiuGG5SYi4tkZRRHSBkDe85S38dEerofhBhohvFDsGCTYJh

Index 2: Full Stack
Address: 5E24XT6U2jvSNZe6gyZdgEGQkvNy59SY6ptDprMisrY8Dvsd

Index 3: Fintech
Address: 5DmcwEMXrSxoGp6NKraDJHXxw4E6ZwmuMrpeggCvQqS5PLEe

Index 4: Bittensor Universe
Address: 5DotNcrAQwCrmv6bEzyhEpgczHUsWyRc9yY4PCGM7u2G6yYE

============================================================
```

### Delegate to an Index

#### Interactive Mode (Recommended for Beginners)

Simply run the command and follow the prompts:

```bash
python contrib/miner_cli/miner_cli.py delegate
```

**Interactive Flow:**
1. Displays available indexes
2. Prompts for index number (0-4)
3. Prompts for wallet name (coldkey)
4. Prompts for wallet hotkey
5. Shows delegation details
6. Asks for confirmation
7. Executes the delegation

**Example Session:**
```
============================================================
Available TrustedStake Indexes
============================================================
[... indexes listed ...]

Enter index number (0-4): 0

Enter wallet name (coldkey): my-coldkey
Enter wallet hotkey: my-hotkey

🔄 Delegating to Index 0: TSBCSI
Address: 5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr

📝 Wallet: my-coldkey
Coldkey: 5C...

⚠️  This will add TSBCSI as a proxy delegate. Continue? (y/N): y

⏳ Adding proxy delegate...
Proxy type: Staking
Enter your password: 
Decrypting...

✅ Successfully delegated to TSBCSI!
Block hash: 0x...

💡 Note: ~0.1 TAO has been locked as a proxy reserve.
This will be refunded when you undelegate.
```

#### With Command-Line Arguments

For scripting or automation:

```bash
python contrib/miner_cli/miner_cli.py delegate \
    --index 0 \
    --wallet.name my-coldkey \
    --wallet.hotkey my-hotkey
```

#### Skip Confirmation Prompt

Add `--yes` or `-y` to skip the confirmation:

```bash
python contrib/miner_cli/miner_cli.py delegate \
    --index 0 \
    --wallet.name my-coldkey \
    --wallet.hotkey my-hotkey \
    --yes
```

#### Use Different Network

Default is `finney`. To use testnet or local:

```bash
python contrib/miner_cli/miner_cli.py delegate \
    --index 0 \
    --wallet.name my-coldkey \
    --wallet.hotkey my-hotkey \
    --network test
```

### Undelegate from an Index

#### Interactive Mode

```bash
python contrib/miner_cli/miner_cli.py undelegate
```

#### With Arguments

```bash
python contrib/miner_cli/miner_cli.py undelegate \
    --index 0 \
    --wallet.name my-coldkey \
    --wallet.hotkey my-hotkey
```

**Example Output:**
```
🔄 Undelegating from Index 0: TSBCSI
Address: 5DyGP1DhWyg4vqxBRK4WcurKhVr2sLvrk488zwpdAX1pcCXr

📝 Wallet: my-coldkey
Coldkey: 5C...

⚠️  This will remove TSBCSI as a proxy delegate. Continue? (y/N): y

⏳ Removing proxy delegate...
Proxy type: Staking
Enter your password: 
Decrypting...

✅ Successfully undelegated from TSBCSI!
Block hash: 0x...

💡 Note: The ~0.1 TAO proxy reserve has been refunded.
⚠️  You may need to manually unstake your TAO from the underlying subnets.
```

## Command Reference

### Global Options

```
-h, --help    Show help message and exit
```

### Commands

#### `list`

Lists all available TrustedStake indexes with their addresses.

**Syntax:**
```bash
python contrib/miner_cli/miner_cli.py list
```

**Arguments:** None

---

#### `delegate`

Adds an index as a proxy delegate to start earning rewards.

**Syntax:**
```bash
python contrib/miner_cli/miner_cli.py delegate [OPTIONS]
```

**Options:**
- `--index INDEX` - Index number to delegate to (0-4). Optional in interactive mode.
- `--wallet.name NAME` - Wallet name (coldkey). Optional in interactive mode.
- `--wallet.hotkey HOTKEY` - Wallet hotkey. Optional in interactive mode.
- `--network {finney,test,local}` - Bittensor network (default: finney)
- `--yes`, `-y` - Skip confirmation prompt

**Examples:**
```bash
# Interactive mode
python contrib/miner_cli/miner_cli.py delegate

# With all arguments
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default

# Skip confirmation
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default --yes

# Use testnet
python contrib/miner_cli/miner_cli.py delegate --index 0 --wallet.name default --wallet.hotkey default --network test
```

---

#### `undelegate`

Removes an index as a proxy delegate to stop staking.

**Syntax:**
```bash
python contrib/miner_cli/miner_cli.py undelegate [OPTIONS]
```

**Options:** Same as `delegate` command

**Examples:**
```bash
# Interactive mode
python contrib/miner_cli/miner_cli.py undelegate

# With all arguments
python contrib/miner_cli/miner_cli.py undelegate --index 0 --wallet.name default --wallet.hotkey default

# Skip confirmation
python contrib/miner_cli/miner_cli.py undelegate --index 0 --wallet.name default --wallet.hotkey default --yes
```

## What Happens When You Delegate

1. ✅ **Adds Proxy**: The index is added as a "Staking" proxy delegate
2. 💰 **Reserve Lock**: ~0.1 TAO is locked as a proxy reserve (automatically refunded on undelegate)
3. ⏳ **Pending Status**: Your position shows "Pending" until the hourly rebalancer runs
4. 📈 **Start Earning**: You begin earning rewards based on: `score = S × (1 + 0.25 × ln(1 + D/30))`
   - S = Stake amount in TAO
   - D = Duration in days

## What Happens When You Undelegate

1. ✅ **Removes Proxy**: The proxy delegate is removed
2. 💰 **Reserve Refund**: The ~0.1 TAO proxy reserve is automatically refunded
3. ⚠️ **Manual Unstaking**: You may need to manually unstake your TAO from underlying subnets using `btcli st remove`

## Supported Indexes

| Index | Name | Description |
|-------|------|-------------|
| 0 | TSBCSI | Broad market index |
| 1 | Top 10 | Top performing subnets |
| 2 | Full Stack | Diversified portfolio |
| 3 | Fintech | Financial subnets |
| 4 | Bittensor Universe | Comprehensive coverage |

## Security & Safety

### Non-Custodial Design
- ✅ You maintain full control of your funds
- ✅ The index can only stake/unstake on your behalf
- ✅ The index **cannot transfer** your funds
- ✅ Your coldkey remains secure under your control

### Confirmation Prompts
- All operations require confirmation (unless `--yes` is used)
- Clear display of what will happen before execution
- Shows wallet addresses and index details

### Proxy Reserve
- ~0.1 TAO is locked when you delegate (Substrate requirement)
- This is **not a fee** - it's automatically refunded when you undelegate
- The reserve is required by the Bittensor blockchain protocol

---

### "Proxy registration not found" Error (on undelegate)
**Problem:** No proxy delegation exists for this index

**Solution:** You may have already undelegated, or the proxy type doesn't match. The CLI uses "Staking" proxy type.

---

### Position Shows "Pending"
**This is normal!**

The TrustedStake rebalancer runs hourly to invest your TAO into constituent subnets. Wait up to 1 hour for your position to become active.

---

### Proxy Reserve Not Refunded
**This is automatic!**

The proxy reserve is automatically refunded when you remove the proxy. If you don't see it immediately, wait a few blocks for the transaction to finalize.

## Technical Details

### Proxy Type
The CLI uses `"Staking"` proxy type for both add and remove operations. This is the correct proxy type for TrustedStake delegations.

### Substrate Calls
- **Add Proxy**: `Proxy.add_proxy(delegate, proxy_type="Staking", delay=0)`
- **Remove Proxy**: `Proxy.remove_proxy(delegate, proxy_type="Staking", delay=0)`

### Index Configuration
Index IDs and labels are imported from `ETF/core/constants.py`:
```python
from ETF.core.constants import INDEX_IDS, INDEX_LABEL
```

This ensures consistency with the rest of the subnet codebase.

### Error Handling
- Validates index range (0-4)
- Checks for empty wallet inputs
- Displays detailed error messages from blockchain
- Includes full traceback for debugging

## Monitoring Your Position

After delegating, monitor your position at:
- **TrustedStake App**: https://app.trustedstake.ai/strat

You can view:
- Staked positions
- Accumulated duration
- Rewards earned
- Portfolio composition

## Support & Resources

- **Subnet FAQ**: [/Docs/FAQ.md](../../Docs/FAQ.md)
- **TrustedStake Docs**: https://trustedstake.gitbook.io/trustedstake/
- **TrustedStake App**: https://app.trustedstake.ai/strat
- **Bittensor Docs**: https://docs.learnbittensor.org/

---

**Note:** This CLI tool is an alternative method for managing delegations. The primary method is through the [TrustedStake web app](https://app.trustedstake.ai/strat).
