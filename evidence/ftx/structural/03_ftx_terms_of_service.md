---
source_url: https://www.coindesk.com/policy/2023/10/16/sbf-trial-what-did-ftxs-terms-of-service-say-about-customer-funds | https://www.axios.com/2022/11/12/ftx-terms-service-trading-customer-funds
date: 2022 (ToS in effect at time of collapse)
description: FTX Terms of Service explicitly promised customer fund segregation — the structural document proving that commingling was contractual fraud, not ambiguity
---

# FTX Terms of Service — Customer Fund Handling

## What the Terms of Service Actually Said

FTX's Terms of Service contained explicit language about customer fund protection. Key provisions:

### Ownership Clause
> "Title to your Digital Assets shall at all times remain with you and shall not transfer to FTX Trading."

### Non-Property Clause
> "None of the Digital Assets in your Account are the property of, or shall or may be loaned to, FTX Trading; FTX Trading does not represent or treat Digital Assets in User's Accounts as belonging to FTX Trading."

### Segregation Principle
FTX stated that it "segregated customer assets from FTX's own assets as a general principle."

### Prohibition on Lending
The ToS explicitly stated that customer digital assets would not be "loaned to" FTX Trading. This directly prohibited the practice of using customer funds for Alameda's trading operations.

## What Actually Happened

Despite these explicit contractual promises:

1. **Customer funds were commingled** with FTX corporate funds and Alameda Research funds
2. **Customer deposits were used** to extend a line of credit to Alameda Research
3. **Customer funds were invested** in non-permitted investments through Alameda
4. **Approximately $8 billion** in customer funds were misappropriated
5. **Alameda had a secret "backdoor"** — an exemption from FTX's auto-liquidation system, allowing it to borrow from customer deposits without limit

## Why This Is Structural (Not Just Empirical)

The ToS is a structural document because it defines what the system **should** look like. It establishes the contractual framework under which customers deposited funds. This enables several analytical paths:

### 1. Contract vs. Reality Gap Analysis
A system that reads the ToS and then observes on-chain evidence of commingling can identify the gap — a strong fraud signal. The ToS says "we don't touch your funds." The blockchain shows funds flowing from customer wallets to Alameda. The contradiction is structural proof of fraud.

### 2. Fiduciary Duty Establishment
Courts subsequently found that the ToS language created a **fiduciary relationship** between FTX and its customers. FTX wasn't just a marketplace — by promising to hold and protect customer assets, it took on a duty of care. This transforms the legal analysis from "caveat emptor" to "breach of trust."

### 3. The "Exchange vs. Broker" Question
FTX marketed itself as an exchange (a platform where users trade with each other) but functioned partly as a custodian (holding user assets). The ToS language confirms the custodial function. This matters because exchanges have different legal obligations than custodians.

## The Alameda Backdoor

Perhaps the most damning structural detail (revealed during the criminal trial):

Alameda Research had a special account status on FTX that:
- Exempted it from the auto-liquidation system (other users would be automatically liquidated if their margin fell below requirements — Alameda would not)
- Allowed it to maintain a **negative balance** — effectively borrowing from FTX (i.e., from customer deposits) without limit
- This was coded into FTX's systems, making it a structural feature, not an operational accident

This is why "the exchange and the trading firm were supposed to be separate" was always a fiction — the code itself connected them.

## Regulatory Context

At the time of collapse:
- FTX.com (international) was regulated by the Securities Commission of The Bahamas — which had limited oversight capacity
- FTX.US (American) was registered as a money services business
- Neither jurisdiction required the kind of regular audits that would have caught the commingling
- The CFTC subsequently obtained a $12.7 billion judgment ($8.7B restitution + $4B disgorgement)

## Sources

- CoinDesk: "SBF Trial: What Did FTX's Terms of Service Say About Customer Funds?" (October 16, 2023)
- Axios: "FTX's terms-of-service forbid trading with customer funds" (November 12, 2022)
- CoinDesk: "FTX Violated Its Own Terms of Service and Misused User Funds, Lawyers Say" (November 10, 2022)
- CFTC: "CFTC Obtains $12.7 Billion Judgment Against FTX and Alameda" (August 2024)
- Alpaca/FTX.US: FTX.US Terms of Service archived document
