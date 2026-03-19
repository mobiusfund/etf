# Tasks

## Completed

### Add RealPaysFee opt-in to miner CLI tooling - 2026-03-19
- Added `proxy_utils.py` with shared chain query utilities and TrustedStake delegate allowlist
- Added `status` command: read-only proxy & RealPaysFee status checker (no signing)
- Added `enable-real-pays-fee` command: standalone RealPaysFee enable for existing proxied users
- Auto-enable RealPaysFee in `delegate` flow (new users get it enabled automatically)
- Added version safety checks (hard-fail on vulnerable bittensor packages)
- Added `--network test` support across all commands (defaults to finney/mainnet)
- Created `test_proxy_utils.py` with unit tests for all proxy utilities
- Updated `test_miner_cli.py` with tests for new commands and auto-enable behavior
- Updated `README.md` with full documentation for all new features
