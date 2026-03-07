"""
Run Credit Suisse investigation and cache the results.

This script runs the full LangGraph investigation with real Gemini API calls
and saves the complete case file for demo playback.
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime

# Phase 6: LangGraph
from graph.investigation_graph import compiled_graph

# Trigger
from triggers.credit_suisse import get_cs_trigger_signal


async def run_and_cache_investigation():
    """
    Run full Credit Suisse investigation and cache results.
    """
    print("=" * 80)
    print("CREDIT SUISSE INVESTIGATION - FULL RUN WITH CACHING")
    print("=" * 80)

    # Get trigger
    trigger = get_cs_trigger_signal()

    print(f"\n📋 Trigger:")
    print(f"  Entity: {trigger['entity']}")
    print(f"  Event: {trigger['event']}")
    print(f"  Date: {trigger['date']}")
    print(f"  Magnitude: {trigger['magnitude']}")

    # Create initial state
    initial_state = {
        "trigger_signal": trigger,
        "entity": trigger["entity"],
        "current_cycle": 0,
        "max_cycles": 5,  # Full investigation
    }

    print(f"\n🚀 Starting LangGraph execution...")
    print(f"  Max cycles: {initial_state['max_cycles']}")

    start_time = datetime.now()

    try:
        # Execute graph
        print(f"\n⏳ Executing investigation (this will take 3-5 minutes)...")
        result = await compiled_graph.ainvoke(initial_state)

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        print(f"\n✅ Investigation complete!")
        print(f"  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")

        # Extract case file
        case_file = result.get("case_file", {})

        if not case_file:
            print("\n⚠️  No case file generated (investigation may have been demoted)")
            return

        # Print summary
        print(f"\n📊 Investigation Summary:")
        print(f"  Status: {case_file.get('status', 'UNKNOWN')}")
        print(f"  Cycles completed: {len(case_file.get('cycle_history', []))}")
        print(f"  Active hypotheses: {len(case_file.get('active_hypotheses', []))}")
        print(f"  Eliminated hypotheses: {len(case_file.get('eliminated_hypotheses', []))}")
        print(f"  Evidence collected: {len(case_file.get('evidence_collected', []))}")
        print(f"  Cross-modal flags: {len(case_file.get('cross_modal_flags', []))}")

        # Calculate total tokens
        total_tokens = sum(
            cycle.get("token_usage", {}).get("total", 0)
            for cycle in case_file.get("cycle_history", [])
        )
        print(f"  Total tokens used: {total_tokens:,}")

        # Show alert
        alert = case_file.get("alert", {})
        if alert:
            print(f"\n🚨 Alert:")
            print(f"  Level: {alert.get('level', 'UNKNOWN')}")
            print(f"  Severity: {alert.get('severity', 'UNKNOWN')}")
            print(f"  Summary: {alert.get('summary', 'N/A')}")

        # Show surviving hypotheses
        active = case_file.get("active_hypotheses", [])
        if active:
            print(f"\n✅ Surviving Hypotheses:")
            for h in active:
                print(f"  {h['id']}: {h['name']} (score: {h.get('score', 0.0):.2f})")

        # Show eliminations
        eliminated = case_file.get("eliminated_hypotheses", [])
        if eliminated:
            print(f"\n❌ Eliminated Hypotheses:")
            for h in eliminated[:5]:  # Show first 5
                print(f"  {h['id']}: {h['name']}")
                print(f"    Killed by: {h.get('killed_by_atom', 'N/A')}")
                print(f"    Reason: {h.get('reason', 'N/A')[:80]}...")

        # Save cached run
        cache_dir = Path(__file__).parent / "corpus" / "cached"
        cache_dir.mkdir(parents=True, exist_ok=True)

        cache_file = cache_dir / "credit_suisse_full_run.json"

        # Prepare cached data
        cached_data = {
            "metadata": {
                "entity": trigger["entity"],
                "trigger_date": trigger["date"],
                "investigation_run_date": start_time.isoformat(),
                "duration_seconds": duration,
                "total_tokens": total_tokens,
            },
            "trigger": trigger,
            "case_file": case_file,
        }

        # Save to file
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_data, f, indent=2, ensure_ascii=False, default=str)

        print(f"\n💾 Cached investigation saved to:")
        print(f"  {cache_file}")
        print(f"  Size: {cache_file.stat().st_size / 1024:.1f} KB")

        print(f"\n✅ COMPLETE - Ready for demo playback!")

        return cached_data

    except Exception as e:
        print(f"\n❌ Error during investigation: {e}")
        import traceback
        traceback.print_exc()
        raise


async def main():
    try:
        cached_data = await run_and_cache_investigation()

        if cached_data:
            print("\n" + "=" * 80)
            print("SUCCESS - Investigation cached for 1-minute demo")
            print("=" * 80)
            print("\nNext steps:")
            print("1. Test cached endpoint: python test_cached_investigation.py")
            print("2. Start server: python main_phase7.py")
            print("3. Run demo with cached mode for 1-min execution")

    except Exception as e:
        print(f"\n❌ FAILED: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
