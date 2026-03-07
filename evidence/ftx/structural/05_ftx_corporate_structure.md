---
source_url: synthesized from court filings, public corporate records, and pre-crisis reporting
date: ongoing (corporate structure as it existed)
description: FTX/Alameda corporate structure — the organizational anatomy that enabled commingling of funds
---

# FTX / Alameda Research Corporate Structure

This document describes the corporate structure of the FTX empire as it existed before the collapse. The organizational relationships are structural — they define how control and fund flows were architecturally possible.

---

## Key Entities

### FTX Trading Ltd
- **Incorporated**: Antigua and Barbuda
- **Registered**: Bahamas (DARE Act license)
- **Headquarters**: Nassau, Bahamas (from September 2021)
- **Function**: International crypto exchange (FTX.com)
- **Governed by**: English law (per Terms of Service)

### West Realm Shires Services Inc (FTX US)
- **Incorporated**: Delaware, USA
- **Function**: US-facing crypto exchange (FTX.US)
- **Governed by**: Delaware law
- **Registered**: Money Services Business with FinCEN

### Alameda Research LLC
- **Incorporated**: Delaware, USA (originally)
- **Relocated**: Hong Kong, then Bahamas
- **Function**: Proprietary crypto trading firm / market maker
- **CEO**: Caroline Ellison (from 2022, jointly with Sam Trabucco until his departure)
- **Founded**: 2017 by Sam Bankman-Fried
- **Key fact**: Alameda predated FTX — FTX was founded in 2019 specifically to serve Alameda's trading needs

### Approximately 130+ Additional Entities
- FTX Ventures
- FTX Foundation (charitable arm)
- FTX Property Holdings
- Various SPVs for investments
- Multiple offshore holding companies

## Ownership and Control

- **Sam Bankman-Fried** owned approximately 90% of FTX Trading Ltd and approximately 90% of Alameda Research
- **Both entities had the same beneficial owner** — there was no independent board or governance separating them
- FTX had no independent board of directors pre-crisis
- Alameda had no independent board of directors
- Key decisions were made by a small inner circle: SBF, Caroline Ellison, Gary Wang, Nishad Singh

## Structural Vulnerability: The FTX-Alameda Bridge

The critical architectural feature that enabled the crisis:

1. **Alameda had a special account on FTX** with privileges not available to other users
2. Per testimony of CTO Gary Wang, Alameda's account could maintain a **negative balance** — effectively borrowing unlimited funds from FTX
3. This "allow_negative" flag was hidden in the codebase
4. Normal users saw their balances as database entries in the FTX system
5. When users deposited funds, fiat deposits were routed to Alameda-controlled bank accounts (at Silvergate and Deltec banks)
6. Alameda could withdraw these deposits to trade, invest, or spend

## The "Backdoor" (Technical Architecture)

- FTX's internal accounting system tracked customer balances as ledger entries
- Alameda's account had special software exemptions from risk checks
- The $65 billion "allow_negative" credit line was inserted as a code modification, not a contractual arrangement
- This meant there was no paper trail of Alameda "borrowing" customer funds — the system simply allowed it

## Key Investors (Pre-Crisis)

| Investor | Round | Amount | Date |
|----------|-------|--------|------|
| Binance | Seed | Undisclosed | 2019 |
| Sequoia Capital | Series B | Part of $900M | July 2021 |
| Paradigm | Series B | Part of $900M | July 2021 |
| Ontario Teachers' Pension Plan | Series B | ~$75M | July 2021 |
| SoftBank Vision Fund 2 | Series C | Part of $400M | January 2022 |
| Tiger Global | Series B | Undisclosed | July 2021 |
| Temasek (Singapore sovereign wealth) | Series C | Undisclosed | January 2022 |

Post-mortem: All equity investments were written down to zero. The investor list demonstrates the level of institutional endorsement FTX received.

## Auditors

- **FTX Trading Ltd**: Prager Metis (a relatively small firm, later investigated)
- **FTX US**: Armanino LLP
- Neither firm flagged the Alameda relationship or the customer fund commingling
- John Ray III (Chapter 11 CEO) later described the audited financials as unreliable
