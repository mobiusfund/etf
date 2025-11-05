# HODL - The ETF Subnet (SN118): FAQ & Summary

## Summary for Newcomers

Welcome to HODL - The ETF Subnet (SN118). This subnet's mission is to bring mature financial products and services, like ETFs, to the Bittensor ecosystem. It aims to act as a market-stabilizing force, provide liquidity, and reward long-term investment conviction in other Bittensor subnets.

For miners, the process is **"zero-code."** You do not need to run any complex software or have specific hardware. Your "mining" performance is based on the amount of TAO you have staked and the duration of that stake in one of the supported, non-custodial TrustedStake indexes. Your funds remain in your control at all times.

---

## Frequently Asked Questions (FAQ)

#### For more FAQ regarding TrustedStake please see the [FAQ](https://trustedstake.gitbook.io/trustedstake/basics/frequently-asked-questions)

### Section 1: The Basics & Subnet Mission

#### Q: What is the purpose of Subnet 118?
**A:** The subnet's mission is to offer financial products and services like ETFs, futures, and options to the Bittensor community. This promotes a healthier investment environment by rewarding long-term conviction, providing liquidity, reducing volatility, and helping the dTao ecosystem mature.

#### Q: Who is the team behind this subnet?
**A:** The team is a collaboration between members of TrustedStake and Investing88.

#### Q: Is this a "proof of stake" subnet?
**A:** For now, yes, that is a good way to describe it. Your rewards are based on your stake amount and its duration, not on computational work or AI inference.

### Section 2: How to Mine on Subnet 118

#### Q: How do I start mining? Is there a miner code to run?
**A:** This is a **zero-code subnet for miners**. You do not need to run any specific miner script. The process is:
1.  Register a hotkey on Subnet 118 using standard Bittensor `btcli subnet register --wallet.name <your cold> --wallet.hotkey <your hot>` commands.
2.  Using the **same coldkey** you registered the miner with, delegate your TAO to one of the three supported indexes on the [TrustedStake app](https://app.trustedstake.ai/).

#### Q: What are the hardware or OS requirements?
**A:** No specific hardware is required for mining since there is no code to run. For advanced users who wish to check live scores by running the validator code, the `README.md` file officially supports Ubuntu 22.04, although other operating systems should work.

#### Q: Do I need to add my hotkey somewhere after delegating?
**A:** No. The system works by linking the coldkey you used to register your miner on SN118 with the coldkey you use to delegate on the TrustedStake app. The subnet automatically detects this link.

#### Q: Can I have multiple miners (hotkeys) on one coldkey?
**A:** You can, but it is not recommended. The total emissions for your coldkey will be divided equally among all its registered hotkeys. Therefore, it is most efficient to have only one miner per coldkey, as confirmed by the scoring logic in `ETF/core/functions.py`.

### Section 3: Staking, TrustedStake, and Funds

#### Q: What is TrustedStake? Is it safe?
**A:** [TrustedStake](https://trustedstake.gitbook.io/trustedstake/basics/editor) is a **non-custodial** platform that allows you to delegate your TAO into diversified indexes of Bittensor subnets. The process is non-custodial, meaning neither TrustedStake nor the subnet team ever takes control of your funds. You grant them "staking proxy" permissions, which only allows them to stake and unstake on your behalf. They cannot transfer your funds.

#### Q: How much TAO do I need to start?
**A:** A minimum balance equivalent to 2 TAO is required to delegate. This can be free TAO, root TAO, or staked alpha on other subnets.

#### Q: Which indexes are supported for mining rewards?
**A:** You must stake your coldkey in one of the three supported indexes to receive emissions. According to `ETF/core/constants.py`, these are:
*   **Index 0:** TSBCSI
*   **Index 1:** Top 10
*   **Index 2:** Full Stack

#### Q: I delegated my TAO. Why does the status say "Pending"?
**A:** "Pending" means you are waiting for the hourly rebalancer to trigger. This process will invest your TAO into the constituent subnets of the index you chose. It can take up to an hour, but occasionally longer if the market metrics dont allow for it or the backend is under maintenance.

#### Q: Why was ~0.1 TAO locked from my wallet when I delegated?
**A:** This is a temporary ["proxy reserve lock"](https://wiki.polkadot.com/learn/learn-proxies/) required by the Bittensor blockchain protocol when you authorize a staking proxy. It is not a fee. This amount is automatically refunded to you when you withdraw and remove the proxy.

#### Q: Can I add more TAO to my position later? Does it reset my stake duration?
**A:** Yes, you can add more TAO at any time by simply sending more TAO to the delegated wallet. It will be automatically added to your position. This **does not** reset your stake duration (`D` in the scoring formula).

#### Q: How do I withdraw my TAO? Are there lockups?
**A:** There are no lockups. You can withdraw at any time via the TrustedStake app. When you "withdraw," you revoke the proxy permission. Note that this does **not** automatically unstake your TAO from the underlying subnets; you may need to do that manually via `btcli st remove` or your wallet application.

### Section 4: Scoring and Rewards

#### Q: How is my miner score calculated?
**A:** The score is calculated based on your staked TAO amount (S) and the duration of your stake in days (D). The official formula is in the `README.md`:
```math
score = S \cdot \left( 1 + 0.25 \cdot ln \left( 1 + \frac {\ D\ } {\ 30\ } \right) \right)
