---
source_url: synthesized from public domain knowledge of crypto exchange architecture
date: ongoing (permanent market structure)
description: Structural anatomy of centralized crypto exchanges — how order books, custody, and fund flows work. Invariant across market conditions.
---

# Centralized Crypto Exchange Market Structure

This document describes the structural architecture of centralized crypto exchanges like FTX, Binance, and Coinbase. These mechanics are invariant — they define how the system works regardless of market conditions.

---

## Order Book Architecture

Centralized exchanges use a **central limit order book (CLOB)**:
- Buyers and sellers submit limit and market orders
- The exchange's matching engine pairs orders by price-time priority
- Trades execute on the exchange's internal ledger, NOT on-chain
- Settlement is **instant** within the exchange (no blockchain confirmation needed)
- Only deposits and withdrawals touch the actual blockchain

## Custody Model

### Omnibus Wallet (industry standard pre-2022)
- Exchange holds ALL customer assets in a small number of wallets
- Customer "balances" are database entries, not on-chain positions
- The exchange controls the private keys
- Customers have a **contractual claim** on assets, not direct possession
- This model enables commingling: exchange can lend/move customer assets internally

### Proof of Reserves
- Some exchanges publish cryptographic proofs of on-chain holdings
- These proofs show assets but NOT liabilities — they can be gamed
- FTX never published proof of reserves
- Binance began publishing proof of reserves in November 2022 (post-FTX)

## Revenue Model

Exchanges earn from:
- **Trading fees**: 0.01-0.10% per trade (maker/taker model)
- **Withdrawal fees**: Fixed fee per withdrawal
- **Listing fees**: Projects pay to list tokens
- **Lending/margin interest**: Interest on leveraged positions
- **Native token**: Exchange-issued tokens (BNB, FTT) generate revenue through fee discounts and buy-back/burn programs

## Native Token Economics (FTT Model)

Exchange-issued tokens like FTT serve multiple functions:
- **Fee discount**: Holding FTT reduces trading fees on FTX
- **Collateral**: FTT accepted as margin collateral on FTX
- **Buy-back and burn**: Exchange uses 33% of trading revenue to buy and burn tokens
- **Staking rewards**: Holding FTT grants enhanced yields

### Circular Valuation Risk
The value of FTT depends on FTX's trading volume, which depends on user deposits, which depend on confidence in FTX, which depends partly on the value of FTT (used as collateral). This creates a **reflexive loop** where confidence shocks can trigger death spirals.

## Withdrawal Mechanics

- Users request withdrawals via exchange interface
- Exchange processes withdrawal from its omnibus wallet
- Blockchain confirmation times vary (Bitcoin: ~10 min, Ethereum: ~15 sec, Solana: ~0.4 sec)
- Exchanges may impose withdrawal delays for "security" or "processing" — this can mask insolvency
- **Bank run dynamics**: If withdrawals exceed liquid reserves, the exchange must sell illiquid assets or halt withdrawals entirely

## Regulatory Landscape (pre-2022)

### United States
- **SEC**: Claims jurisdiction over tokens that are "securities" (Howey test)
- **CFTC**: Claims jurisdiction over commodity-based tokens (Bitcoin, Ethereum)
- **FinCEN**: Money transmission licensing requirements
- FTX.US was a registered Money Services Business but NOT a registered exchange
- FTX.com (international) was explicitly NOT available to US customers (Terms of Service)

### Bahamas
- **DARE Act (2020)**: Digital Assets and Registered Exchanges Act
- Streamlined licensing for exchanges, wallet providers, token issuers
- FTX Trading Ltd registered under DARE Act
- Securities Commission of the Bahamas: primary regulator

### No Global Standard
- No international regulatory framework for crypto exchanges existed
- Exchanges could "jurisdiction shop" — incorporating in favorable locations
- Most exchanges operated with minimal or no audited financial statements
