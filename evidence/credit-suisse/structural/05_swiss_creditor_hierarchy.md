---
source_url: https://www.fedlex.admin.ch/eli/cc/51/117_121_129/en (Swiss Banking Act)
date: ongoing (permanent law)
description: Swiss insolvency creditor hierarchy for banks — the legal pecking order that determines who gets paid first in a bank failure. This is the structural framework that made the AT1 write-down legally controversial.
---

# Swiss Bank Insolvency — Creditor Hierarchy

The creditor hierarchy in Swiss bank insolvency proceedings determines the order in which claims are satisfied. This hierarchy is fixed by law and does not change with market conditions.

---

## Standard Creditor Hierarchy (Banking Act Art. 37a-37b)

In a standard Swiss bank bankruptcy, claims are satisfied in the following order:

### Class 1 — Privileged Claims
- Privileged depositors (deposits up to CHF 100,000 per depositor)
- Employee wage claims
- Social insurance contributions

### Class 2 — Other Privileged Claims
- Remaining deposit claims (above CHF 100,000)
- Claims of the deposit insurance scheme (Esisuisse)

### Class 3 — Ordinary Claims (Unsecured Senior)
- Senior unsecured bonds
- Senior bail-in bonds (TLAC-eligible)
- Trade creditors
- Other unsecured claims

### Subordinated Claims
- Tier 2 capital instruments (low-trigger)
- Additional Tier 1 capital instruments (AT1/CoCo bonds)

### Equity
- Common equity (CET1) — last to absorb losses

## Swiss Deposit Insurance (Esisuisse)

- Covers deposits up to **CHF 100,000** per depositor per bank
- System capacity: CHF 6 billion (funded by member banks)
- NOT government-guaranteed — funded by industry mutual agreement
- Significantly smaller than the FDIC ($250,000 per depositor, backed by US government)

## Key Structural Tension: AT1 vs Equity in Resolution

Under normal insolvency, AT1 bondholders rank ABOVE equity holders. However, the AT1 prospectus contractual terms (see 01_at1_prospectus_ponv_clause.md) create a separate mechanism:

- The **Viability Event** clause allows FINMA to write down AT1 bonds to zero **independently** of the standard hierarchy
- This creates a scenario where AT1 is wiped out while equity retains value — inverting the normal priority
- The AT1 contractual write-down is a **pre-insolvency** mechanism, triggered before formal bankruptcy proceedings begin
- This is structurally different from a bail-in (which follows the hierarchy)

## FINMA's Resolution Powers (Banking Act Art. 25-37g)

FINMA has broad resolution powers for banks:
- **Protective measures** (Art. 26): Restrict business operations, appoint investigators
- **Restructuring** (Art. 28-32): Convert/write-down capital instruments, transfer assets, create bridge bank
- **Bankruptcy** (Art. 33-37g): Liquidation following the creditor hierarchy above

Key: FINMA can order restructuring measures (including AT1 write-down) WITHOUT triggering formal bankruptcy — this means the standard creditor hierarchy does NOT necessarily apply to AT1 write-downs.
