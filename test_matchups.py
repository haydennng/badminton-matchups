"""
Tests for Badminton Matchup Manager

Basic tests for the core algorithms and functionality.
"""

import unittest
from matchup_generator import MatchupGenerator
from game_valuation import GameValuation, PricingStrategy
from match_storage import MatchStorage
import os
import json


class TestMatchupGenerator(unittest.TestCase):
    def setUp(self):
        self.players = ["Alice", "Bob", "Charlie", "Diana"]
        self.generator = MatchupGenerator(self.players)
    
    def test_initialization(self):
        """Test that generator initializes correctly."""
        self.assertEqual(len(self.generator.players), 4)
        self.assertIn("Alice", self.generator.players)
    
    def test_minimum_players_required(self):
        """Test that at least 4 players are required."""
        with self.assertRaises(ValueError):
            MatchupGenerator(["Alice", "Bob", "Charlie"])
    
    def test_generate_matchup(self):
        """Test generating a single matchup."""
        team1, team2 = self.generator.generate_matchup()
        
        # Check teams have correct size
        self.assertEqual(len(team1), 2)
        self.assertEqual(len(team2), 2)
        
        # Check no overlap between teams
        self.assertEqual(len(set(team1) & set(team2)), 0)
        
        # Check all players are from original list
        all_match_players = set(team1) | set(team2)
        self.assertTrue(all_match_players.issubset(set(self.players)))
    
    def test_generate_session(self):
        """Test generating a full session of matchups."""
        matchups = self.generator.generate_session(2.0, 15)  # 2 hours, 15 min per game
        
        # Should generate 8 games (120 min / 15 min)
        self.assertEqual(len(matchups), 8)
        
        # Check each matchup has required fields
        for match in matchups:
            self.assertIn('game_number', match)
            self.assertIn('team1', match)
            self.assertIn('team2', match)
            self.assertEqual(len(match['team1']), 2)
            self.assertEqual(len(match['team2']), 2)
    
    def test_fairness(self):
        """Test that matchups are distributed fairly."""
        # Generate many games
        matchups = self.generator.generate_session(4.0, 15)
        
        # Count partnerships for each player
        partnership_counts = {player: {} for player in self.players}
        
        for match in matchups:
            for team in [match['team1'], match['team2']]:
                p1, p2 = team
                partnership_counts[p1][p2] = partnership_counts[p1].get(p2, 0) + 1
                partnership_counts[p2][p1] = partnership_counts[p2].get(p1, 0) + 1
        
        # Check that no player is heavily favored
        # (exact fairness depends on number of games, but shouldn't be too skewed)
        for player, partners in partnership_counts.items():
            if partners:
                max_count = max(partners.values())
                min_count = min(partners.values())
                # Difference shouldn't be more than 3 for a 4-hour session
                self.assertLessEqual(max_count - min_count, 3)


class TestGameValuation(unittest.TestCase):
    def test_fixed_pricing(self):
        """Test fixed pricing strategy."""
        valuator = GameValuation(PricingStrategy.FIXED, 10.0)
        value = valuator.calculate_value(1)
        
        self.assertEqual(value['game_value'], 10.0)
        self.assertEqual(value['winner_receives'], 10.0)
    
    def test_escalating_pricing(self):
        """Test escalating pricing strategy."""
        valuator = GameValuation(PricingStrategy.ESCALATING, 10.0)
        
        value1 = valuator.calculate_value(1)
        value2 = valuator.calculate_value(2)
        value3 = valuator.calculate_value(3)
        
        # Values should increase
        self.assertEqual(value1['game_value'], 10.0)
        self.assertEqual(value2['game_value'], 11.0)
        self.assertEqual(value3['game_value'], 12.0)
    
    def test_session_total_fixed(self):
        """Test session total calculation for fixed pricing."""
        valuator = GameValuation(PricingStrategy.FIXED, 5.0)
        total = valuator.calculate_session_total(10)
        
        self.assertEqual(total, 50.0)
    
    def test_base_value_validation(self):
        """Test that base value must be positive."""
        valuator = GameValuation()
        with self.assertRaises(ValueError):
            valuator.set_base_value(-5.0)


class TestMatchStorage(unittest.TestCase):
    def setUp(self):
        """Set up test storage with temporary directory."""
        self.test_dir = "test_data"
        self.storage = MatchStorage(self.test_dir)
    
    def tearDown(self):
        """Clean up test data."""
        import shutil
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
    
    def test_save_and_retrieve_match(self):
        """Test saving and retrieving a match."""
        match_data = {
            'game_number': 1,
            'team1': ['Alice', 'Bob'],
            'team2': ['Charlie', 'Diana'],
            'team1_score': 21,
            'team2_score': 18,
            'game_value': 10.0
        }
        
        match_id = self.storage.save_match(match_data)
        self.assertIsNotNone(match_id)
        
        # Retrieve and verify
        matches = self.storage.get_all_matches()
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['team1'], ['Alice', 'Bob'])
    
    def test_get_matches_by_player(self):
        """Test retrieving matches for a specific player."""
        # Save multiple matches
        self.storage.save_match({
            'team1': ['Alice', 'Bob'],
            'team2': ['Charlie', 'Diana']
        })
        self.storage.save_match({
            'team1': ['Alice', 'Charlie'],
            'team2': ['Bob', 'Diana']
        })
        self.storage.save_match({
            'team1': ['Bob', 'Diana'],
            'team2': ['Charlie', 'Eve']
        })
        
        # Alice should be in 2 matches
        alice_matches = self.storage.get_matches_by_player('Alice')
        self.assertEqual(len(alice_matches), 2)
    
    def test_player_stats(self):
        """Test calculating player statistics."""
        # Save matches with scores
        self.storage.save_match({
            'team1': ['Alice', 'Bob'],
            'team2': ['Charlie', 'Diana'],
            'team1_score': 21,
            'team2_score': 18,
            'game_value': 10.0
        })
        self.storage.save_match({
            'team1': ['Alice', 'Charlie'],
            'team2': ['Bob', 'Diana'],
            'team1_score': 19,
            'team2_score': 21,
            'game_value': 10.0
        })
        
        stats = self.storage.get_player_stats('Alice')
        
        self.assertEqual(stats['total_matches'], 2)
        self.assertEqual(stats['wins'], 1)
        self.assertEqual(stats['losses'], 1)
        self.assertEqual(stats['win_rate'], 50.0)


if __name__ == '__main__':
    print("Running Badminton Matchup Manager Tests\n")
    unittest.main(verbosity=2)
