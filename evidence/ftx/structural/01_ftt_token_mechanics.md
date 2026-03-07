---
source_url: https://coinmarketcap.com/alexandria/article/what-is-ftx-token-ftt-features-tokenomics-and-price-prediction | https://www.nansen.ai/research/blockchain-analysis-the-collapse-of-alameda-and-ftx
date: 2019-2022 (token lifecycle)
description: FTT token mechanics — sourced from CoinMarketCap Alexandria and Nansen research
---

# FTT Token Mechanics and Tokenomics

## Token Supply (from CoinMarketCap Alexandria)

- **Total supply:** "350,000,000 FTT tokens"
- **Circulating supply:** 170,923,766 FTT (as of article publication)
- **Burned tokens:** 13,171,373 FTT burned, with 64,862 additional scheduled
- **Token type:** ERC-20 utility token, created 2019

## Burn Mechanism (from CoinMarketCap)

FTX allocated exchange revenue to buy back and permanently burn FTT: "one-third of which will be utilized to repurchase FTT tokens and later become a part of the burning process." Approximately 33% of transaction fees collected on FTX were allocated toward token buybacks and destruction.

Burns occurred weekly.

## Token Utility (from CoinMarketCap)

- **Trading fee discounts** — tiered discounts based on FTT holdings
- **Collateral for futures positions** — FTT could "serve as collateral for futures positions" using FTX's "centralized collateral pool and universal stablecoin settlement"
- **Staking rewards** — "free withdrawals of ERC20 and ETH daily," maker fee rebates, IEO eligibility, enhanced referral commissions
- **Unstaking requirement:** 14-day lock period before withdrawal

## Supply Concentration (from Nansen on-chain analysis)

Nansen's blockchain analysis showed FTX and Alameda wallets held the vast majority of FTT tokens. The "free float" that actually traded on markets was a small fraction of total supply.

FTX/Alameda controlled approximately ~90% of all FTT tokens through:
- Company reserves
- Locked tokens with vesting schedules
- Tokens held as collateral
- Tokens on Alameda's balance sheet

With ~90% of supply controlled by related entities, the "market cap" was set by the ~10% that traded freely, but "value" was calculated across all 350 million tokens.

## The Alameda Balance Sheet Numbers (from CoinDesk, November 2, 2022)

From the leaked balance sheet (as of June 30, 2022):
- **$3.66 billion** in unlocked FTT (largest single asset)
- **$2.16 billion** in FTT collateral
- **$292 million** in locked FTT (liabilities side)
- **Total FTT exposure: ~$5.82 billion** out of $14.6B total assets = ~40% of all assets

With ~$7.4B in loans and FTT backing a substantial portion, any significant FTT price decline would threaten Alameda's solvency.

## Circular Collateral Structure

The token mechanics created a reflexive loop:
1. FTX/Alameda holds massive FTT positions
2. FTT's price depends on FTX's perceived health and trading volume
3. FTX/Alameda uses FTT as collateral for loans
4. Any threat to FTX → FTT price drops → collateral value drops → margin calls → forced selling → further price drops

Given the supply concentration and collateral usage, any sufficiently large sell pressure (like Binance announcing liquidation of its holdings) would trigger a mathematically inevitable death spiral.

## Sources

- CoinMarketCap Alexandria: "What Is FTX Token (FTT)? Features, Tokenomics and Price Prediction"
- Nansen Research: "Blockchain Analysis: The Collapse of Alameda and FTX"
- CoinDesk (Ian Allison): "Divisions in Sam Bankman-Fried's Crypto Empire Blur on His Trading Titan Alameda's Balance Sheet" (November 2, 2022)
