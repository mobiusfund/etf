<div align="center">

# HODL - The ETF Subnet
### Incentivizing long-term conviction
</div>

## Intro

Please reference our [whitepaper](./Docs/HODL%20-%20The%20ETF%20Subnet.pdf) for a comprehensive overview.

## Roadmap

- V1, Live at launch: HODL ETF
- V2, Q1 2026: ETF Exchange
- V3, Q3 2026: Futures and Options

Transaction fees generated from V2/V3 will have a major percentage committed to automatic buybacks.

## Installation

This subnet is zero code for miners. Please follow the [Bittensor document](https://docs.learnbittensor.org/miners/) to register a hotkey.

#### Setup

```bash
sudo apt update
sudo apt install npm -y
sudo npm install pm2 -g
git clone https://github.com/mobiusfund/etf
cd etf
# optional
python -m venv .venv
. .venv/bin/activate
#
python -m pip install -e .
```

#### Validator

```bash
# optional
. .venv/bin/activate
# quick start
ETF/bin/validator
#
pm2 start neurons/validator.py \
    --name etf-validator -- \
    --wallet.name {coldkey} \
    --wallet.hotkey {hotkey} \
    --netuid 118
```

## Mining

Please stake the miner coldkey in one of the supported [TrustedStake indexes](https://app.trustedstake.ai/strat) in order to receive emissions. Currently supported indexes are: TSBCSI, Top 10, and Full Stack.

Total subnet emissions are equally divided among the supported indexes.

Miner score is calculated using the following formula, where $$S$$ is the coldkey stake amount in Tao, and $$D$$ is the stake duration in days:

```math
\begin{aligned}
& score = S \cdot \left( 1 + 0.25 \cdot ln \left( 1 + \frac {\ D\ } {\ 30\ } \right) \right)
\\
\end{aligned}
```

## License
This repository is licensed under the MIT License.
```text
# The MIT License (MIT)
# Copyright © 2024 Opentensor Foundation

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
```
