# HODL - The ETF Subnet (SN118): FAQ & Summary

## Summary for Newcomers

Welcome to HODL - The ETF Subnet (SN118). This subnet's mission is to bring mature financial products and services, like ETFs and exchange infrastructure, to the Bittensor ecosystem. It acts as a market-stabilizing force, provides liquidity, and rewards long-term investment conviction in other Bittensor subnets.

The subnet has evolved through two phases:

- **V1 (Foundation):** Miners earned emissions by staking TAO into TrustedStake indices‚ as a zero-code, conviction-based model that bootstrapped capital commitment to the Bittensor alpha market.
- **V2 (HODL Exchange):** Miners earn emissions as **Incentivized Market Makers(IMMs)** by filling orders on the HODL Exchange, an escrow-based order book for alpha tokens that is ~85% cheaper than native liquidity pools.

The subnet is currently transitioning from V1 to V2 over approximately four weeks. During the transition period, emissions are split between both mechanisms.

---

## Frequently Asked Questions (FAQ)

#### For more FAQ regarding TrustedStake please see the [FAQ](https://trustedstake.gitbook.io/trustedstake/basics/frequently-asked-questions)

### Section 1: The Basics & Subnet Mission

#### Q: What is Subnet 118 (the HODL Subnet)?

**A:** Subnet 118 (HODL) is revolutionary market infrastructure for the Bittensor ecosystem. It introduces an OTC market with an orderbook that doesn’t exist anywhere else:

The **HODL Exchange** , an escrow-based order book for subnet alpha tokens that is ~85% cheaper than on-chain liquidity pools, protecting subnet token prices by avoiding pool slippage and preventing negative TAO flow.

#### Q: What problem does SN118 solve in the Bittensor ecosystem?

**A:** It directly combats short-term speculation and the "trench warfare" mentality by rewarding long-term conviction. In the new world of Flow-based emissions, HODL provides the critical infrastructure for sustainable TAO Flows by creating a structured trading environment that protects subnet token prices from the volatility of public liquidity pools. The HODL Exchange builds on this by offering traders a dramatically cheaper alternative to on-chain swaps, keeping capital within the ecosystem rather than leaking it to pool slippage and MEV.

#### Q: Who is the team behind this subnet?

**A:** The team is a collaboration between members of TrustedStake and Investing88.

#### Q: Is this a "proof of stake" subnet?

**A:** Under V1, yes ‚ rewards were based on your stake amount and its duration, not on computational work or AI inference. Under V2, miners earn emissions by actively providing liquidity on the HODL Exchange as Incentivized Market Makers (IMMs). No heavy compute or AI models are required, but miners do actively participate in filling orders.

---

### Section 2: How to Mine on Subnet 118

#### Q: How do I start mining under V2 (current)?

**A:** Under V2, miners earn emissions as **Incentivized Market Makers (IMMs)** on the HODL Exchange. You fill buy and sell orders placed by other participants. The more volume you fill, the larger your share of daily emissions.

1. Register a hotkey on Subnet 118 using standard Bittensor `btcli subnet register --wallet.name <your cold> --wallet.hotkey <your hot>` commands.
2. Link your miner's ss58 wallet address to your hotkey.
3. Provide liquidity on the [HODL Exchange](https://exfe-orderbook.vercel.app/) by filling orders.

#### Q: How did mining work under V1?

**A:** V1 was a **zero-code subnet for miners**. You did not need to run any specific miner script. The process was:

1. Register a hotkey on Subnet 118.
2. Using the **same coldkey** you registered the miner with, delegate your TAO to one of the five supported indexes on the [TrustedStake app](https://app.trustedstake.ai/).

V1 is being phased out over ~4 weeks as emissions transition fully to the V2 IMM mechanism.

#### Q: What are the hardware or OS requirements?

**A:** No specific hardware is required for mining under either V1 or V2 ‚ there is no heavy compute to run. For advanced users who wish to check live scores by running the validator code, the `README.md` file officially supports Ubuntu 22.04, although other operating systems should work.

#### Q: Do I need to add my hotkey somewhere after delegating?

**A:** Under V1, no. The system works by linking the coldkey you used to register your miner on SN118 with the coldkey you use to delegate on the TrustedStake app. The subnet automatically detects this link. Under V2, miner attribution is handled through the escrow architecture ‚ the system deterministically identifies who filled each order based on ss58 addresses.

#### Q: Can I have multiple miners (hotkeys) on one coldkey?

**A:** You can, but it is not recommended. The total emissions for your coldkey will be divided equally among all its registered hotkeys. Therefore, it is most efficient to have only one miner per coldkey, as confirmed by the scoring logic in `ETF/core/functions.py`.

---

### Section 3: The HODL Exchange

#### Q: What is the HODL Exchange?

**A:** The HODL Exchange is an escrow-based order book for Bittensor alpha tokens. Unlike on-chain liquidity pools, it is a proper order book where buyers and sellers are matched through dedicated escrow wallets. Every trade is ~85% cheaper than swapping through the native AMM pools.

#### Q: How does the escrow system work?

**A:** Each order generates a unique escrow wallet identified by its ss58 address:
- You transfer assets to escrow ‚ alpha tokens if selling, TAO if buying. The order size equals what you deposit.
- Order type is determined by comparing your ss58 to the escrow ss58 , if they match, you opened the order; if they differ, you're filling it.
- The backend executes a two-way escrow transfer with sanity checks. Zero escrow balance = order won't execute.

#### Q: How are HODL Exchange fees calculated?

**A:** The exchange charges ~15% of the slippage you would have paid using the native on-chain liquidity pool:

```
Fee = 0.15 √ó Slippage_pool
```

This scales proportionally with order size:

| Order Size | Pool Slippage | HODL Fee | User Savings |
|-----------|--------------|----------|-------------|
| 1 TAO | ~0.5% | ~0.075% | 85% |
| 100 TAO | ~5% | ~0.75% | 85% |
| 1,000 TAO | ~20% | ~3% | 85% |

#### Q: Where do the exchange fees go?

**A:** After operating expenses, all fees collected in TAO are used to buy back SN118 alpha from the liquidity pool. This creates a direct flywheel: more exchange volume leads to more buyback pressure leads to higher token value.

#### Q: What is an Incentivized Market Maker (IMM)?

**A:** An IMM is a miner who earns SN118 alpha emissions by filling orders on the HODL Exchange. Unlike passive LPs in an AMM, IMMs are not forced into fixed-ratio positions and are not subject to impermanent loss. They can deploy inventory they already hold from other activity in the Bittensor ecosystem ‚ for example, mining alpha on another subnet and selling it on the HODL Exchange.

#### Q: Why are IMMs better than passive LPs?

**A:** IMMs receive alpha emissions as a baseline incentive regardless of whether trading fees exceed impermanent loss. They choose what inventory to deploy and at what price, rather than being locked into a pool ratio. This makes market making on the HODL Exchange more capital-efficient and lower-risk than traditional LP positions.

---

### Section 4: Staking, Trading, and Time Value (V1, Old Model as of 3/10/2025)

#### Q: What is TrustedStake? Is it safe?

**A:** [TrustedStake](https://trustedstake.gitbook.io/trustedstake/basics/editor) is a **non-custodial** platform that allows you to delegate your TAO into diversified indexes of Bittensor subnets. The process is non-custodial, meaning neither TrustedStake nor the subnet team ever takes control of your funds. You grant them "staking proxy" permissions, which only allows them to stake and unstake on your behalf. They cannot transfer your funds.

#### Q: How much TAO do I need to start?

**A:** A minimum balance equivalent to 2 TAO is required to delegate. This can be free TAO, root TAO, or staked alpha on other subnets.

#### Q: Which indexes are supported for mining rewards?

**A:** Under V1, you must stake your coldkey in one of the five supported indexes to receive emissions. According to `ETF/core/constants.py`, these are:

* **Index 0:** TSBCSI
* **Index 1:** Top 10
* **Index 2:** Full Stack
* **Index 3:** FinTech
* **Index 4:** Bittensor Universe

#### Q: I delegated my TAO. Why does the status say "Pending"?

**A:** "Pending" means you are waiting for the rebalancer which triggers every four hours. This process will invest your TAO into the constituent subnets of the index you chose. It can take up to an hour, but occasionally longer if the market metrics don't allow for it or the backend is under maintenance.

#### Q: Why was ~0.1 TAO locked from my wallet when I delegated?

**A:** This is a temporary ["proxy reserve lock"](https://wiki.polkadot.com/learn/learn-proxies/) required by the Bittensor blockchain protocol when you authorize a staking proxy. It is not a fee. This amount is automatically refunded to you when you withdraw and remove the proxy.

#### Q: Can I add more TAO to my position later? Does it reset my stake duration?

**A:** Yes, you can add more TAO at any time by simply sending more TAO to the delegated wallet. It will be automatically added to your position. This **does not** reset your stake duration (`D` in the scoring formula).

#### Q: How do I withdraw my TAO? Are there lockups?

**A:** There are no lockups. You can withdraw at any time via the TrustedStake app. When you "withdraw," you revoke the proxy permission. Note that this does **not** automatically unstake your TAO from the underlying subnets; you may need to do that manually via `btcli st remove` or your wallet application.

#### Q: What is "Time Value" or "Duration"?

**A:** Time = value. When you hold an incentivized TrustedStake index on SN118, you accumulate duration. This represents the future Alpha emissions your position is entitled to on the duration curve. This duration creates a tradable premium over the base value of the TAO staked in your index. The longer you hold, the more your position is worth.

#### Q: How does trading a miner position work?

**A:** Let's say you stake 1,000 TAO in an index. After several months, your position has accumulated significant duration. On the HODL secondary market, you can sell this entire position for a premium ‚Äî for example, 1,050 TAO. That extra 50 TAO is the tradable time value you earned through conviction.

#### Q: Why should I pay a premium for a miner position?

**A:** When you buy a position for a premium (e.g., 1,050 TAO for a 1,000 TAO stake), you are acquiring more than just the underlying TAO. You get:
- A diversified, blue-chip subnet portfolio.
- Zero slippage/MEV on the transfer.
- The future Alpha emissions attached to that position's accumulated duration.
- Instant exposure without having to build a position from scratch.

---

### Section 5: Scoring, Tokenomics, and Rewards

#### Q: How is my miner score calculated under V2 (current)?

**A:** At launch, emission allocation is based solely on **FillVolume** ‚ the total TAO equivalent of fills you execute per epoch:

```
Emissions_i = (FillVolume_i / Œ£ FillVolume_j) √ó Daily_IMM_Emissions
```

Your share of emissions equals your share of total fill volume. Additional scoring dimensions will be introduced incrementally as the exchange matures.

#### Q: What additional scoring dimensions are planned?

**A:** The full target formula is multiplicative: `Score = FillVolume √ó SpreadQuality √ó TwoSidedMultiplier √ó ConsistencyMultiplier`. Each dimension can be activated independently as real exchange data informs calibration:

- **SpreadQuality** ‚ rewards tighter fills relative to pool price. At launch, orders don't carry a spread, so this effectively equals 1.
- **TwoSidedMultiplier** ‚ rewards miners providing liquidity on both buy and sell sides. At launch, sell-side flow is expected to dominate, so activating this prematurely would penalize the natural early market structure.
- **ConsistencyMultiplier** ‚ rewards persistent liquidity over sporadic bursts. Will be calibrated using real exchange data.

The multiplicative structure means a zero on any active dimension zeroes the entire score ‚ a powerful anti-gaming property once multiple dimensions are live.

#### Q: How was my score calculated under V1?

**A:** Under V1, the score was calculated based on your staked TAO amount (S) and the duration of your stake in days (D):

```math
score = S \cdot \left( 1 + 0.25 \cdot ln \left( 1 + \frac {\ D\ } {\ 30\ } \right) \right)
```

#### Q: What gives SN118 Alpha its value?

**A:** SN118 Alpha is a direct representation of the economic output produced by the subnet. Its value is driven by the flywheel effect of its buyback mechanism. After operating expenses, all fees generated from HODL Exchange trading activity are used to buy back SN118 Alpha from the market. This creates constant buying pressure and reduces the circulating supply, benefiting all Alpha holders. As the exchange grows volume, the flywheel accelerates — more volume means more fees means more buyback pressure. The token's value is ultimately tied to the real economic activity the subnet facilitates, not speculation.

#### Q: How does the subnet prevent wash trading?

**A:** Multiple layers of defense:
- **Minimum order sizes** raise the capital required per cycle.
- **Fee drag** ‚ the ~15% slippage-based fee creates a cost on every round trip that a wash trader absorbs without economic gain.
- **Planned: Spread floor** ‚ when SpreadQuality is activated, fills below a minimum distance from pool price earn zero.
- **Planned: Multiplicative scoring** ‚ once multiple dimensions are active, gaming all of them simultaneously approaches the cost of genuine market making.

#### Q: How does SN118 align incentives?

**A:** Under V1, the protocol rewarded long-term holding, encouraging miners to support the health of Bittensor's best subnets by investing in them. Under V2, miners are directly rewarded for providing liquidity that benefits every trader on the exchange — deeper books, tighter execution, and better prices. The trading fee gives the token tangible value grounded in real exchange activity, moving it beyond market speculation and sentiment. The buyback mechanism ensures that all trading activity benefits SN118 Alpha holders. Each phase aligns emissions with the subnet's current operational need.

---

### Section 6: V1 ‚ V2 Transition

#### Q: What is the transition timeline?

**A:** The expansion from V1 to V2 occurs gradually over approximately four weeks:

| Week | IMM (V2) | Index Staking (V1) | Notes |
|------|----------|-------------------|-------|
| 1 | 25% | 75% | Exchange launches, IMM scoring goes live |
| 2 | 50% | 50% | Monitor volume and market maker participation |
| 3 | 75% | 25% | Majority of emissions reward active market making |
| 4 | 100% | 0% | Full transition to V2 complete |

Timeline may be adjusted based on adoption metrics and market maker participation levels.

#### Q: What happens to my V1 staking position during the transition?

**A:** Your V1 position continues to earn emissions during the transition, but at a decreasing share as the allocation shifts toward V2 IMMs. By Week 4, all emissions flow to the IMM mechanism.

#### Q: Can I participate in both V1 and V2 during the transition?

**A:** Yes. During the transition, you can maintain your TrustedStake index position (V1) while also filling orders on the HODL Exchange (V2).

---

### Section 7: Roadmap & Vision

#### Q: What are the next steps for SN118's development?

**A:** V2 (HODL Exchange) is now live, bringing escrow-based alpha trading to the Bittensor ecosystem with Incentivized Market Makers earning emissions for providing liquidity. The scoring mechanism will expand iteratively as exchange volume and data grow. V3 will introduce futures and options in Q3 2026, adding more sophisticated financial tooling to the ecosystem. Transaction fees from V2/V3 are committed to automatic SN118 alpha buybacks.

#### Q: How does SN118 contribute to the broader dTAO economy?

**A:** It provides the critical financial infrastructure for a mature, stable dTAO economy. By turning conviction into a tradable asset, protecting subnets from speculative volatility and outflows, and now offering an exchange that is ~85% cheaper than on-chain pools with no MEV risk, HODL creates a sustainable environment where long-term investment is rewarded and trading is efficient ‚ benefiting the entire Bittensor network.
