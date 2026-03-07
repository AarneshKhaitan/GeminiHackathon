---
source_url: synthesized from public domain knowledge of crypto exchange architecture
date: ongoing (permanent market structure)
description: Anatomy of centralized crypto exchanges — order books, custody models, fund flows, regulatory landscape
---

# Centralized Crypto Exchange Architecture

---

## Order Book

Centralized exchanges use a **central limit order book (CLOB)**:
- Buyers and sellers submit limit and market orders
- The exchange's matching engine pairs orders by price-time priority
- Trades execute on the exchange's internal ledger, not on-chain
- Settlement is instant within the exchange (no blockchain confirmation needed)
- Only deposits and withdrawals touch the actual blockchain

## Custody Model

### Omnibus Wallet (industry standard pre-2022)
- Exchange holds all customer assets in a small number of wallets
- Customer "balances" are database entries, not on-chain positions
- The exchange controls the private keys
- Customers have a contractual claim on assets, not direct possession

### Proof of Reserves
- Some exchanges publish cryptographic proofs of on-chain holdings
- These proofs show assets but not liabilities
- Not an industry requirement as of 2022

## Revenue Model

Exchanges earn from:
- **Trading fees**: 0.01-0.10% per trade (maker/taker model)
- **Withdrawal fees**: Fixed fee per withdrawal
- **Listing fees**: Projects pay to list tokens
- **Lending/margin interest**: Interest on leveraged positions
- **Native token**: Exchange-issued tokens (BNB, FTT) generate revenue through fee discounts and buy-back/burn programs

## Native Token Economics (FTT Model)

Exchange-issued tokens serve multiple functions:
- **Fee discount**: Holding FTT reduces trading fees on FTX
- **Collateral**: FTT accepted as margin collateral on FTX
- **Buy-back and burn**: Exchange uses 33% of trading revenue to buy and burn tokens
- **Staking rewards**: Holding FTT grants enhanced yields

The value of an exchange token depends on the exchange's trading volume. Trading volume depends on user deposits. User deposits depend partly on confidence in the exchange.

## Withdrawal Mechanics

- Users request withdrawals via exchange interface
- Exchange processes withdrawal from its omnibus wallet
- Blockchain confirmation times vary (Bitcoin: ~10 min, Ethereum: ~15 sec, Solana: ~0.4 sec)
- Exchanges may impose withdrawal delays for "security" or "processing"

## Regulatory Landscape (pre-2022)

### United States
- **SEC**: Claims jurisdiction over tokens that are "securities" (Howey test)
- **CFTC**: Claims jurisdiction over commodity-based tokens (Bitcoin, Ethereum)
- **FinCEN**: Money transmission licensing requirements
- FTX.US was a registered Money Services Business

### Bahamas
- **DARE Act (2020)**: Digital Assets and Registered Exchanges Act
- Streamlined licensing for exchanges, wallet providers, token issuers
- FTX Trading Ltd registered under DARE Act
- Securities Commission of the Bahamas: primary regulator

### No Global Standard
- No international regulatory framework for crypto exchanges existed as of 2022
- Exchanges incorporated in favorable jurisdictions
- Most exchanges operated without audited financial statements
