---
source_url: https://coinmarketcap.com/alexandria/article/what-is-ftx-token-ftt-features-tokenomics-and-price-prediction | https://www.nansen.ai/research/blockchain-analysis-the-collapse-of-alameda-and-ftx
date: 2019-2022 (token lifecycle)
description: FTT token mechanics — burn model, supply distribution, and circular collateral structure that created reflexive death spiral risk
---

# FTT Token Mechanics and Tokenomics

## What is FTT?

FTT was an ERC-20 utility token created by FTX exchange in 2019. It was the native token of the FTX platform, serving as the exchange's primary loyalty and utility mechanism.

## Token Utility

FTT provided holders with:
- **Trading fee discounts** — tiered discounts based on FTT holdings (up to 60% off)
- **Collateral for futures positions** — FTT could be used as margin collateral on FTX
- **Staking rewards** — holders could stake FTT for additional benefits (maker fee rebates, bonus votes, IEO tickets)
- **Socialized loss protection** — FTT stakers received insurance fund protection
- **Early access** — to new token listings and IEO participation

## Token Supply and Distribution

- **Total supply:** 350 million FTT (at creation)
- **Initial circulating supply:** ~95 million (~27% of total)
- **Company allocation:** FTX and Alameda controlled approximately **~90% of all FTT tokens** through a combination of:
  - Company reserves
  - Locked tokens with vesting schedules
  - Tokens held as collateral
  - Tokens on Alameda's balance sheet

This concentration is the critical structural fact. With ~90% of supply controlled by FTX/Alameda entities, the "market cap" of FTT was a fiction — the price was set by the ~10% that actually traded freely, but the "value" was calculated across all 350 million tokens.

## Buy-and-Burn Mechanism

FTX allocated a portion of exchange revenue to buy back and permanently burn FTT tokens:
- **33%** of trading fees
- **10%** of net additions to the insurance fund
- **5%** of other fees and revenue

Burns occurred weekly. By November 2022, approximately 27 million FTT had been burned. This mechanism was designed to create deflationary pressure and support the token price.

The burn mechanism created a dependency: FTT's value proposition depended on FTX generating revenue, which depended on FTX being a successful exchange, which depended on having adequate capital, which (circularly) was backed by FTT holdings.

## The Circular Collateral Problem

This is the critical structural vulnerability — a reflexive death spiral:

### The Loop
1. FTX/Alameda holds massive FTT positions (~$5.8B on Alameda's balance sheet alone)
2. FTT's price depends on FTX's perceived health and trading volume
3. FTX/Alameda uses FTT as **collateral** for loans and margin positions
4. If FTX shows signs of trouble → FTT price drops
5. FTT price drops → collateral value drops → margin calls / loan recalls
6. Forced selling of FTT to meet obligations → further price drops
7. Further price drops → more collateral shortfalls → death spiral

### Why This Is Structural, Not Empirical

This isn't a "market observation" — it's a **mathematical property** of the system. The moment you know:
- FTX/Alameda holds ~90% of FTT supply
- They use FTT as collateral for billions in loans
- FTT's value depends on FTX's continued operation

...you can simulate the death spiral *before it happens*. Given any sufficiently large sell pressure on FTT (like Binance announcing it would sell its holdings), the reflexive collapse is inevitable.

### The Alameda Balance Sheet Numbers

From the leaked balance sheet (as of June 30, 2022):
- **$3.66 billion** in unlocked FTT (largest single asset)
- **$2.16 billion** in FTT collateral (third largest asset)
- **$292 million** in locked FTT (on liabilities side)
- **Total FTT exposure: ~$6.1 billion** out of $14.6B total assets = **42% of all assets**

With ~$7.4B in loans and FTT backing a substantial portion of them, any significant FTT price decline would render Alameda insolvent.

### Comparison to Traditional Finance

In traditional finance, a bank using its own stock as collateral for loans is prohibited or heavily restricted precisely because of this reflexive risk. The crypto ecosystem had no such restrictions. FTX was effectively using "magic beans" it created as collateral for real-dollar loans — a structure that could only survive as long as no one tested it.

## Supply Concentration Data

Source: Nansen on-chain analysis

Nansen's blockchain analysis showed that FTX and Alameda wallets held the vast majority of FTT tokens. The "free float" that actually traded on markets was a small fraction of total supply, meaning:
- Market cap figures vastly overstated real liquidity
- Any large seller (like Binance with ~$529M in FTT) would crash the price
- There was no depth in the order book to absorb large sells

## Sources

- CoinMarketCap Alexandria: "What Is FTX Token (FTT)? Features, Tokenomics and Price Prediction"
- Nansen Research: "Blockchain Analysis: The Collapse of Alameda and FTX"
- CoinDesk: "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet" (Nov 2, 2022)
