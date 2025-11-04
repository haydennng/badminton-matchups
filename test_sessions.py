#!/usr/bin/env python3
"""
Quick test script to verify session implementation
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_api():
    print("=" * 60)
    print("Testing Session-Based Badminton Matchups API")
    print("=" * 60)
    
    # Test 1: Get current session
    print("\n1. Testing GET /api/sessions/current...")
    response = requests.get(f"{BASE_URL}/api/sessions/current")
    if response.status_code == 200:
        current_session = response.json()
        print(f"   ✓ Current session: {current_session['session_id']}")
        print(f"   ✓ Date: {current_session['date']}")
        print(f"   ✓ Match count: {current_session['match_count']}")
        print(f"   ✓ Players: {', '.join(current_session['players']) if current_session['players'] else 'None yet'}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
        return
    
    # Test 2: Get all sessions
    print("\n2. Testing GET /api/sessions...")
    response = requests.get(f"{BASE_URL}/api/sessions")
    if response.status_code == 200:
        sessions = response.json()
        print(f"   ✓ Found {len(sessions)} session(s)")
        for session in sessions[:3]:  # Show first 3
            print(f"     - {session['date']}: {session['match_count']} matches, {len(session['players'])} players")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 3: Record a test match
    print("\n3. Testing POST /api/matches (recording a test match)...")
    test_match = {
        "team1": ["Hayden", "Jonny"],
        "team2": ["Danny", "Phi"],
        "team1_score": 21,
        "team2_score": 19,
        "game_value": 2
    }
    response = requests.post(
        f"{BASE_URL}/api/matches",
        json=test_match,
        headers={"Content-Type": "application/json"}
    )
    if response.status_code == 200:
        match = response.json()
        print(f"   ✓ Match recorded: {match['match_id']}")
        print(f"   ✓ Session: {match['session_id']}")
        print(f"   ✓ Game number: {match['game_number']}")
    else:
        print(f"   ✗ Failed: {response.status_code} - {response.text}")
    
    # Test 4: Get updated current session
    print("\n4. Testing session update after match...")
    response = requests.get(f"{BASE_URL}/api/sessions/current")
    if response.status_code == 200:
        updated_session = response.json()
        print(f"   ✓ Match count now: {updated_session['match_count']}")
        print(f"   ✓ Players: {', '.join(updated_session['players'])}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    # Test 5: Get session detail
    print("\n5. Testing GET /api/sessions/{session_id}...")
    response = requests.get(f"{BASE_URL}/api/sessions/{current_session['session_id']}")
    if response.status_code == 200:
        session_detail = response.json()
        print(f"   ✓ Session has {len(session_detail['matches'])} match(es)")
        if session_detail['matches']:
            last_match = session_detail['matches'][-1]
            print(f"   ✓ Last match: {' & '.join(last_match['team1'])} vs {' & '.join(last_match['team2'])}")
    else:
        print(f"   ✗ Failed: {response.status_code}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Open http://localhost:5000/history to view sessions")
    print("2. Open http://localhost:5000/matchups to record matches")
    print("3. Try recording more matches and deleting them")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("✗ Error: Could not connect to server")
        print("  Make sure the Flask server is running: python app.py")
    except Exception as e:
        print(f"✗ Error: {e}")
