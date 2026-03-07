#!/usr/bin/env python3
"""
Test WebSocket connection between frontend and backend.
Simulates what the frontend does when starting an investigation.
"""
import asyncio
import json
import websockets

async def test_websocket():
    """Connect to WebSocket and start an investigation."""
    uri = "ws://localhost:8000/ws/test_session"

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connected")

            # Send investigation start command (simulating frontend)
            start_command = {
                "trigger": "Bank run accelerated by social media",
                "entity": "Silicon Valley Bank",
                "ticker": "SIVB"
            }
            await websocket.send(json.dumps(start_command))
            print(f"✓ Sent start command: {start_command['entity']}")

            # Receive messages for 5 seconds
            print("\n=== WebSocket Messages ===")
            messages_received = 0

            try:
                while messages_received < 15:  # Get first 15 messages
                    message = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                    data = json.loads(message)
                    messages_received += 1

                    # Pretty print key message types
                    msg_type = data.get("type", "UNKNOWN")
                    if msg_type == "SESSION_STARTED":
                        print(f"  {messages_received}. {msg_type} - Entity: {data['entity']}, Tier: {data['tier']}")
                    elif msg_type == "TIER_ESCALATED":
                        print(f"  {messages_received}. {msg_type} - T{data['from']} → T{data['to']}")
                    elif msg_type == "CYCLE_STARTED":
                        print(f"  {messages_received}. {msg_type} - Cycle {data['cycle_number']}")
                    elif msg_type == "HYPOTHESIS_GENERATED":
                        print(f"  {messages_received}. {msg_type} - {data['hypothesis']['label']}")
                    elif msg_type == "EVIDENCE_ATOM_ARRIVED":
                        print(f"  {messages_received}. {msg_type} - {data['atom']['id']}")
                    elif msg_type == "AGENT_STATUS_CHANGED":
                        print(f"  {messages_received}. {msg_type} - {data['agent']}: {data['status']}")
                    else:
                        print(f"  {messages_received}. {msg_type}")

            except asyncio.TimeoutError:
                print(f"\n✓ Received {messages_received} messages (timed out waiting for more)")

            print(f"\n✓ WebSocket test completed - {messages_received} messages received")

    except Exception as e:
        print(f"✗ WebSocket error: {e}")
        return False

    return True

if __name__ == "__main__":
    print("Testing WebSocket connection to backend...\n")
    result = asyncio.run(test_websocket())
    exit(0 if result else 1)
