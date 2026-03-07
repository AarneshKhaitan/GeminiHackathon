# Evidence Package — Hypothesis Elimination Engine

Evidence for two historical financial crises. The engine receives **structural docs + pre-cutoff input** and must reason toward the correct diagnosis. **Ground truth** validates the output.

## Events

### Credit Suisse (March 2023)
- **Input cutoff:** March 16, 2023 (after SNB facility draw)
- **The challenge:** On March 15-16, consensus was CS would survive — regulators endorsed it, analysts defended it, emergency liquidity was deployed. The system must disagree with consensus using structural reasoning.
- **Ground truth:** UBS forced acquisition at CHF 0.76/share. CHF 16B AT1 bonds written to zero. FINMA emergency ordinance.

### FTX (November 2022)
- **Input cutoff:** November 8, 2022 (through Binance LOI)
- **The challenge:** On November 8, the dominant narrative was "Binance will rescue FTX, crisis over." SBF was still saying "assets are fine." The system must reason through the counter-evidence and identify likely fraud from structural analysis.
- **Ground truth:** Binance walked away. $8B customer funds misappropriated. SBF convicted on 7 counts.

## Folder Structure

```
evidence/
├── credit-suisse/
│   ├── structural/      (contracts, regulations, legal powers — no cutoff)
│   ├── empirical/       (pre-March 16 articles, data, video — what the engine sees)
│   ├── ground_truth/    (March 18-19 resolution — what actually happened)
│   └── manifest.md
├── ftx/
│   ├── structural/      (token mechanics, ToS, balance sheet — no cutoff)
│   ├── empirical/       (pre-November 9 articles, data, tweets — what the engine sees)
│   ├── ground_truth/    (bankruptcy, trial, conviction — what actually happened)
│   └── manifest.md
└── README.md
```

## Counter-Evidence

~30-40% of input files are COUNTER-EVIDENCE — analyst defenses, regulatory reassurances, management denials, rescue announcements. Pre-cutoff, this was the dominant narrative. The system must reason through it, not ignore it.
