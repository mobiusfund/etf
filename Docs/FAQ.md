# HODL - The ETF Subnet (SN118): FAQ & Summary

## Summary for Newcomers

Welcome to HODL - The ETF Subnet (SN118). This subnet's mission is to bring mature financial products and services, like ETFs, to the Bittensor ecosystem. It aims to act as a market-stabilizing force, provide liquidity, and reward long-term investment conviction in other Bittensor subnets.

For miners, the process is **"zero-code."** You do not need to run any complex software or have specific hardware. Your "mining" performance is based on the amount of TAO you have staked and the duration of that stake in one of the supported, non-custodial TrustedStake indexes. Your funds remain in your control at all times.

---

## Frequently Asked Questions (FAQ)

#### For more FAQ regarding TrustedStake please see the [FAQ](https://trustedstake.gitbook.io/trustedstake/basics/frequently-asked-questions)

### Section 1: The Basics & Subnet Mission

#### Q: What is Subnet 118 (the HODL Subnet)?
**A:** Subnet 118 (HODL) is a revolutionary market infrastructure for the Bittensor ecosystem. It introduces two markets that don’t exist anywhere else:
1. A secondary market for @TrustedStake subnet index positions, allowing you to trade complete miner slots with their embedded time value.
2. An OTC market for subnet alpha tokens, which protects subnet token prices by avoiding liquidity pools and preventing negative TAO flow.

#### Q: What problem does SN118 solve in the Bittensor ecosystem?
**A:** It directly combats short-term speculation and the “trench warfare” mentality by rewarding long-term conviction. In the new world of Flow-based emissions, HODL provides the critical infrastructure for sustainable TAO inflows by creating a structured trading environment that protects subnet token prices from the volatility of public liquidity pools.

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

### Section 3: Staking, Trading, and Time Value

#### Q: What is TrustedStake? Is it safe?
**A:** [TrustedStake](https://trustedstake.gitbook.io/trustedstake/basics/editor) is a **non-custodial** platform that allows you to delegate your TAO into diversified indexes of Bittensor subnets. The process is non-custodial, meaning neither TrustedStake nor the subnet team ever takes control of your funds. You grant them "staking proxy" permissions, which only allows them to stake and unstake on your behalf. They cannot transfer your funds.

#### Q: How much TAO do I need to start?
**A:** A minimum balance equivalent to 2 TAO is required to delegate. This can be free TAO, root TAO, or staked alpha on other subnets.

#### Q: Which indexes are supported for mining rewards?
**A:** You must stake your coldkey in one of the five supported indexes to receive emissions. According to `ETF/core/constants.py`, these are:
*   **Index 0:** TSBCSI
*   **Index 1:** Top 10
*   **Index 2:** Full Stack
*   **Index 3:** FinTech
*   **Index 4:** Bittensor Universe

#### Q: I delegated my TAO. Why does the status say "Pending"?
**A:** "Pending" means you are waiting for the rebalancer which triggers every four hours. This process will invest your TAO into the constituent subnets of the index you chose. It can take up to an hour, but occasionally longer if the market metrics dont allow for it or the backend is under maintenance.

#### Q: Why was ~0.1 TAO locked from my wallet when I delegated?
**A:** This is a temporary ["proxy reserve lock"](https://wiki.polkadot.com/learn/learn-proxies/) required by the Bittensor blockchain protocol when you authorize a staking proxy. It is not a fee. This amount is automatically refunded to you when you withdraw and remove the proxy.

#### Q: Can I add more TAO to my position later? Does it reset my stake duration?
**A:** Yes, you can add more TAO at any time by simply sending more TAO to the delegated wallet. It will be automatically added to your position. This **does not** reset your stake duration (`D` in the scoring formula).

#### Q: How do I withdraw my TAO? Are there lockups?
**A:** There are no lockups. You can withdraw at any time via the TrustedStake app. When you "withdraw," you revoke the proxy permission. Note that this does **not** automatically unstake your TAO from the underlying subnets; you may need to do that manually via `btcli st remove` or your wallet application.

#### Q: What is “Time Value” or “Duration”?
**A:** Time = value. When you hold an incentivized TrustedStake index on SN118, you accumulate duration. This represents the future Alpha emissions your position is entitled to on the duration curve. This duration creates a tradable premium over the base value of the TAO staked in your index. The longer you hold, the more your position is worth.

#### Q: How does trading a miner position work?
**A:** Let’s say you stake 1,000 TAO in an index. After several months, your position has accumulated significant duration. On the HODL secondary market, you can sell this entire position for a premium—for example, 1,050 TAO. That extra 50 TAO is the tradable time value you earned through conviction.

#### Q: Why should I pay a premium for a miner position?
**A:** When you buy a position for a premium (e.g., 1,050 TAO for a 1,000 TAO stake), you are acquiring more than just the underlying TAO. You get:
•A diversified, blue-chip subnet portfolio.
•Zero slippage/MEV on the transfer.
•The future Alpha emissions attached to that position’s accumulated duration.
•Instant exposure without having to build a position from scratch.

### Section 4: Tokenomics, Scoring, and Rewards

#### Q: How is my miner score calculated?
**A:** The score is calculated based on your staked TAO amount (S) and the duration of your stake in days (D). The official formula is in the `README.md`:
```math
score = S \cdot \left( 1 + 0.25 \cdot ln \left( 1 + \frac {\ D\ } {\ 30\ } \right) \right)
```

#### Q: What are the fees on the exchange?
**A:** The protocol is funded by two fee streams:
1. Transaction Fee (0.5%): Applied to all trades on both the index and OTC markets.
2. Performance Fee (20%): Applied only to the realized premium from selling a TrustedStake index position. You keep 80% of the premium you created.
Using the example in Section 3, on the 50 TAO premium, the protocol would collect a 10 TAO performance fee (20%), and you would keep 40 TAO as your profit.

#### Q: What gives SN118 Alpha its value?
**A:** Its value is driven by the flywheel effect of its buyback mechanism. 100% of the fees generated from trading activity are used to automatically buy back SN118 Alpha from the market. This creates constant buying pressure and reduces the circulating supply, benefiting all Alpha holders.

#### Q: How does SN118 align incentives?
**A:** By rewarding long-term holding, the protocol encourages miners to support the health of the subnets they are invested in. The OTC market protects subnet token prices from volatility, and the buyback mechanism ensures that all trading activity benefits SN118 Alpha holders. It creates a system where conviction is profitable for everyone.

### Section 5: Roadmap & Vision

#### Q: What are the next steps for SN118’s development?
**A:** The immediate roadmap includes launching the V2 ETF Exchange in January 2026, which will bring full OTC market functionality online. Following that, V3 will introduce futures and options in Q3 2026, adding more sophisticated financial tooling to the ecosystem.

#### Q: How does SN118 contribute to the broader dTAO economy?
**A:** It provides the critical financial infrastructure for a mature, stable dTAO economy. By turning conviction into a tradable asset and protecting subnets from speculative volatility and outflows, HODL creates a sustainable environment where long-term investment is rewarded, benefiting the entire Bittensor network.
