#!/usr/bin/env python3
"""
Test Credit Suisse investigation flow.
Tests the full backend flow with Credit Suisse data.
"""
import asyncio
import json
import websockets

async def test_credit_suisse_investigation():
    """Run a full Credit Suisse investigation and collect results."""
    uri = "ws://localhost:8000/ws/test_cs_investigation"

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connected")

            # Send Credit Suisse investigation start command
            start_command = {
                "trigger": "CDS spreads widened 300bps; major shareholder refuses additional capital injection",
                "entity": "Credit Suisse",
                "ticker": "CS"
            }
            await websocket.send(json.dumps(start_command))
            print(f"✓ Sent start command: {start_command['entity']}\n")

            # Track investigation progress
            session_started = False
            tier_escalated = False
            cycle_count = 0
            hypotheses_generated = 0
            hypotheses_eliminated = 0
            evidence_atoms = 0
            convergence_reached = False

            print("=== Investigation Progress ===\n")

            try:
                while True:
                    message = await asyncio.wait_for(websocket.recv(), timeout=120.0)
                    data = json.loads(message)
                    msg_type = data.get("type", "UNKNOWN")

                    if msg_type == "SESSION_STARTED":
                        session_started = True
                        print(f"✓ Session started - Entity: {data['entity']}, Tier: {data['tier']}")

                    elif msg_type == "TIER_ESCALATED":
                        tier_escalated = True
                        print(f"✓ Tier escalated: T{data['from']} → T{data['to']}")

                    elif msg_type == "CYCLE_STARTED":
                        cycle_count = data['cycle_number']
                        print(f"\n--- Cycle {cycle_count} started ---")

                    elif msg_type == "HYPOTHESIS_GENERATED":
                        hypotheses_generated += 1
                        print(f"  • Hypothesis: {data['hypothesis']['label']}")

                    elif msg_type == "HYPOTHESIS_ELIMINATED":
                        hypotheses_eliminated += 1
                        print(f"  ✗ Eliminated: {data['id']} (Reason: {data['kill_reason'][:80]}...)")

                    elif msg_type == "EVIDENCE_ATOM_ARRIVED":
                        evidence_atoms += 1
                        if evidence_atoms <= 5:  # Show first 5
                            atom = data['atom']
                            print(f"  • Evidence {atom['id']}: {atom['source']}")

                    elif msg_type == "CYCLE_COMPLETE":
                        print(f"  ✓ Cycle {data['cycle_number']} complete - {data['survivors']} survivors ({data['duration_ms']}ms)")

                    elif msg_type == "CONVERGENCE_REACHED":
                        convergence_reached = True
                        diagnosis = data['diagnosis']
                        print(f"\n{'='*60}")
                        print(f"✓ CONVERGENCE REACHED")
                        print(f"{'='*60}")
                        print(f"Level: {diagnosis['level']}")
                        print(f"Severity: {diagnosis['severity']}")
                        print(f"Headline: {diagnosis['headline']}")
                        print(f"Surviving Hypotheses: {diagnosis['survivingHypotheses']}")
                        print(f"{'='*60}\n")

                    elif msg_type == "INVESTIGATION_COMPLETE":
                        print("✓ Investigation complete\n")
                        break

            except asyncio.TimeoutError:
                print("\n✗ Investigation timed out")
                return False

            # Summary
            print("=== Investigation Summary ===")
            print(f"Session started: {session_started}")
            print(f"Tier escalated: {tier_escalated}")
            print(f"Cycles completed: {cycle_count}")
            print(f"Hypotheses generated: {hypotheses_generated}")
            print(f"Hypotheses eliminated: {hypotheses_eliminated}")
            print(f"Evidence atoms collected: {evidence_atoms}")
            print(f"Convergence reached: {convergence_reached}")

            success = all([session_started, tier_escalated, cycle_count > 0,
                          hypotheses_generated > 0, evidence_atoms > 0, convergence_reached])

            if success:
                print("\n✓ All checks passed - Integration working correctly!")
            else:
                print("\n✗ Some checks failed - Review output above")

            return success

    except Exception as e:
        print(f"\n✗ Error during investigation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Testing Credit Suisse investigation flow...\n")
    result = asyncio.run(test_credit_suisse_investigation())
    exit(0 if result else 1)
