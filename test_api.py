#!/usr/bin/env python3
"""
Quick test script to verify the API endpoints work correctly
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_add_players():
    """Add test players"""
    print("\n=== Adding Players ===")
    players = ["Alice", "Bob", "Charlie", "Diana"]
    
    for player in players:
        response = requests.post(
            f"{BASE_URL}/api/players",
            json={"name": player}
        )
        print(f"Added {player}: {response.status_code}")
    
    # Get all players
    response = requests.get(f"{BASE_URL}/api/players")
    print(f"Current players: {response.json()}")

def test_record_match():
    """Test recording a match"""
    print("\n=== Recording Match ===")
    
    match_data = {
        "team1": ["Alice", "Bob"],
        "team2": ["Charlie", "Diana"],
        "team1_score": 21,
        "team2_score": 18,
        "game_value": 3
    }
    
    print(f"Sending: {json.dumps(match_data, indent=2)}")
    
    response = requests.post(
        f"{BASE_URL}/api/matches",
        json=match_data
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Match recorded successfully!")
    else:
        print("❌ Failed to record match")

def test_get_matches():
    """Get all matches"""
    print("\n=== Getting All Matches ===")
    
    response = requests.get(f"{BASE_URL}/api/matches")
    matches = response.json()
    
    print(f"Total matches: {len(matches)}")
    for match in matches:
        print(f"  Game #{match['game_number']}: {' & '.join(match['team1'])} vs {' & '.join(match['team2'])} - ${match['game_value']}")

if __name__ == "__main__":
    print("Testing Badminton Matchup API")
    print("Make sure Flask app is running on http://localhost:5000")
    
    try:
        # Test if server is running
        response = requests.get(f"{BASE_URL}/api/session")
        print(f"✅ Server is running")
        
        test_add_players()
        test_record_match()
        test_get_matches()
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure Flask is running!")
    except Exception as e:
        print(f"❌ Error: {e}")
