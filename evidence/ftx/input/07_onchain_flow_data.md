---
source_url: https://www.nansen.ai/research/blockchain-analysis-the-collapse-of-alameda-and-ftx
date: 2022-11-06 to 2022-11-12
description: On-chain flow data — FTX wallet depletion, Alameda-FTX fund movements, $600M unauthorized drain
---

# On-Chain Flow Data — FTX Collapse

Primary source: Nansen Research — "Blockchain Analysis: The Collapse of Alameda and FTX"
Additional: Etherscan, Arkham Intelligence, on-chain analysts on Twitter

## FTX Wallet Depletion

Stablecoin reserves:
- FTX.com stablecoin holdings dropped from approximately $1.5 billion to near zero between Nov 6-8
- USDC, USDT, BUSD all drained as FTX processed withdrawals
- When stablecoins ran out, FTX sent ETH and other crypto to meet requests
- Eventually even those ran dry

Net outflows by day:
- Nov 6: ~$653M net outflow
- Nov 7: ~$1.5-2B net outflow (estimated)
- Nov 8: Withdrawals halted partway through the day
- Total before halt: $5-6 billion over 72 hours

## Alameda-FTX Flow

On-chain analysts observed bidirectional flows between known Alameda and FTX wallet addresses:

Funds flowing FROM Alameda TO FTX — suggesting FTX was pulling Alameda's reserves to cover customer withdrawals. Real-time evidence that the two entities were connected, contradicting years of claims that they were separate.

Funds flowing FROM FTX TO unknown wallets — some identified as Alameda's wallets, others were new addresses.

## The $600M Unauthorized Transactions (Nov 11-12)

Within hours of the Chapter 11 filing on November 11:

- Over $600 million in crypto moved out of FTX wallets to previously unknown addresses
- Movements on Ethereum, BSC, and other chains
- Mix of ETH, stablecoins, and other tokens
- Some tokens immediately swapped on DEXes (Uniswap, 1inch)
- Etherscan labeled the draining address as "FTX Accounts Drainer"

Some transfers looked like theft (swapping to ETH through DEXes, common laundering pattern). Some were later attributed to the Bahamas Securities Commission ordering assets moved to government custody. Full accounting took months.

## Tools for verification:

- Etherscan.io — Ethereum transaction explorer
- Nansen.ai — on-chain analytics
- Arkham Intelligence — wallet labeling and flow tracking
