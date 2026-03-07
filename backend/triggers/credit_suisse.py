"""
Credit Suisse Investigation Trigger - Demo

Use this trigger for the 1-minute demo.
"""

CREDIT_SUISSE_TRIGGER = {
    "entity": "Credit Suisse",
    "event": "Q4 2022 earnings reveal CHF 110.5 billion deposit outflows",
    "date": "2023-02-09",
    "magnitude": {
        "deposit_outflows": "CHF 110.5 billion (Q4 2022)",
        "net_loss": "CHF 7.3 billion annual loss (2022)",
        "assets_under_management": "Down 19.9% YoY to CHF 1,293.6 billion",
        "wealth_management_outflows": "~15% of AUM fled in Q4 alone",
    },
    "background": {
        "restructuring_announced": "October 2022 - CHF 4B capital raise, 9K job cuts, IB split",
        "saudi_investment": "Saudi National Bank takes 9.9% stake calling it 'a steal' (Oct 2022)",
        "prior_scandals": "Archegos ($5.5B loss) + Greensill ($10B frozen) in March 2021",
        "stock_trajectory": "Down 80% from Feb 2021 peak (CHF 14 → CHF 2.80 at earnings)",
    },
    "trigger_event_description": (
        "On February 9, 2023, Credit Suisse reported Q4 2022 earnings revealing CHF 110.5 billion "
        "in net new asset outflows during the quarter - approximately 8% of total assets under management. "
        "The bank disclosed that outflows 'substantially exceeded' Q3 levels, with two-thirds concentrated "
        "in October 2022 (immediately after restructuring announcement). Wealth Management alone saw ~15% "
        "of AUM flee in Q4. Despite completing a CHF 4 billion capital raise and reporting adequate capital "
        "ratios (CET1 14.1%), the magnitude of deposit flight revealed that the October restructuring plan "
        "failed to restore client confidence. The bank reported CHF 7.3 billion in annual losses for 2022."
    ),
    "why_investigate": (
        "Credit Suisse meets Tier 2 escalation criteria: "
        "(1) G-SIB with systemic importance, "
        "(2) CHF 110.5B deposit outflows = classic early warning of bank run, "
        "(3) Outflows occurred AFTER capital raise - restructuring failed to restore confidence, "
        "(4) 15% wealth management AUM flight in single quarter unprecedented for G-SIB, "
        "(5) Total assets down 30% YoY signals structural balance sheet stress, "
        "(6) Capital ratios adequate but deposit flight indicates solvency vs. confidence crisis."
    ),
    "outcome": (
        "Credit Suisse continued to experience instability. One month later (March 2023), SVB collapse "
        "triggered renewed panic. Saudi National Bank's 'absolutely not' interview (March 15) caused "
        "30% intraday stock crash. Swiss regulators orchestrated forced UBS merger on March 19, 2023 "
        "(38 days after earnings). AT1 bondholders suffered complete write-down ($17 billion). "
        "First G-SIB resolution since 2008."
    ),
}


# For API calls
def get_cs_trigger_signal():
    """
    Returns Credit Suisse trigger in the format expected by the investigation API.
    """
    return {
        "entity": CREDIT_SUISSE_TRIGGER["entity"],
        "event": CREDIT_SUISSE_TRIGGER["event"],
        "date": CREDIT_SUISSE_TRIGGER["date"],
        "magnitude": CREDIT_SUISSE_TRIGGER["magnitude"]["deposit_outflows"],
        "description": CREDIT_SUISSE_TRIGGER["trigger_event_description"],
    }


# Compact version for UI
CS_TRIGGER_COMPACT = {
    "entity": "Credit Suisse",
    "event": "Q4 earnings reveal CHF 110.5B deposit outflows",
    "date": "2023-02-09",
    "magnitude": "CHF 110.5B outflows (8% of AUM)",
    "context": "Post-restructuring confidence crisis + CHF 7.3B annual loss",
}


if __name__ == "__main__":
    import json
    print("=" * 80)
    print("CREDIT SUISSE DEMO TRIGGER")
    print("=" * 80)
    print("\nFull trigger:")
    print(json.dumps(CREDIT_SUISSE_TRIGGER, indent=2))
    print("\n" + "=" * 80)
    print("API format:")
    print(json.dumps(get_cs_trigger_signal(), indent=2))
    print("\n" + "=" * 80)
    print("Compact format:")
    print(json.dumps(CS_TRIGGER_COMPACT, indent=2))
