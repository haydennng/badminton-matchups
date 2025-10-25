"""
Matchup Generator for Fair 2v2 Badminton Games

This module generates balanced matchups ensuring:
- Players rotate partners evenly
- Players face different opponents
- Fair distribution across multiple games
"""

import itertools
import random
from typing import List, Tuple, Set
from collections import defaultdict


class MatchupGenerator:
    def __init__(self, players: List[str]):
        """
        Initialize the matchup generator with a list of players.
        
        Args:
            players: List of player names (minimum 4 required)
        """
        if len(players) < 4:
            raise ValueError("At least 4 players are required for 2v2 matches")
        
        self.players = players
        self.partnership_count = defaultdict(int)
        self.opponent_count = defaultdict(int)
        
    def _get_pair_key(self, player1: str, player2: str) -> Tuple[str, str]:
        """Create a sorted tuple key for a pair of players."""
        return tuple(sorted([player1, player2]))
    
    def _score_matchup(self, team1: Tuple[str, str], team2: Tuple[str, str]) -> float:
        """
        Score a potential matchup based on how balanced it is.
        Lower scores are better (less repeated pairings).
        """
        p1, p2 = team1
        p3, p4 = team2
        
        # Count how many times these partnerships have occurred
        partnership_score = (
            self.partnership_count[self._get_pair_key(p1, p2)] +
            self.partnership_count[self._get_pair_key(p3, p4)]
        )
        
        # Count how many times these players have faced each other
        opponent_score = (
            self.opponent_count[self._get_pair_key(p1, p3)] +
            self.opponent_count[self._get_pair_key(p1, p4)] +
            self.opponent_count[self._get_pair_key(p2, p3)] +
            self.opponent_count[self._get_pair_key(p2, p4)]
        )
        
        # Combine scores (weight partnerships more heavily)
        return partnership_score * 2 + opponent_score
    
    def _update_history(self, team1: Tuple[str, str], team2: Tuple[str, str]):
        """Update partnership and opponent history after a match."""
        p1, p2 = team1
        p3, p4 = team2
        
        # Update partnerships
        self.partnership_count[self._get_pair_key(p1, p2)] += 1
        self.partnership_count[self._get_pair_key(p3, p4)] += 1
        
        # Update opponents
        self.opponent_count[self._get_pair_key(p1, p3)] += 1
        self.opponent_count[self._get_pair_key(p1, p4)] += 1
        self.opponent_count[self._get_pair_key(p2, p3)] += 1
        self.opponent_count[self._get_pair_key(p2, p4)] += 1
    
    def generate_matchup(self) -> Tuple[Tuple[str, str], Tuple[str, str]]:
        """
        Generate a single fair matchup.
        
        Returns:
            Tuple of two teams, each team is a tuple of two player names
        """
        # Get all possible team combinations
        all_teams = list(itertools.combinations(self.players, 2))
        
        best_matchup = None
        best_score = float('inf')
        
        # Try all possible matchups
        for team1 in all_teams:
            remaining_players = [p for p in self.players if p not in team1]
            for team2 in itertools.combinations(remaining_players, 2):
                score = self._score_matchup(team1, team2)
                if score < best_score:
                    best_score = score
                    best_matchup = (team1, team2)
        
        if best_matchup:
            self._update_history(best_matchup[0], best_matchup[1])
        
        return best_matchup
    
    def generate_session(self, duration_hours: float, minutes_per_game: int = 15) -> List[dict]:
        """
        Generate matchups for an entire session.
        
        Args:
            duration_hours: Total session duration in hours
            minutes_per_game: Average time per game in minutes
            
        Returns:
            List of matchup dictionaries with team and game info
        """
        total_minutes = duration_hours * 60
        num_games = int(total_minutes / minutes_per_game)
        
        matchups = []
        for game_num in range(1, num_games + 1):
            team1, team2 = self.generate_matchup()
            matchups.append({
                'game_number': game_num,
                'team1': list(team1),
                'team2': list(team2),
                'estimated_start_time': (game_num - 1) * minutes_per_game
            })
        
        return matchups
    
    def reset_history(self):
        """Reset partnership and opponent tracking."""
        self.partnership_count.clear()
        self.opponent_count.clear()
    
    def get_stats(self) -> dict:
        """Get current statistics about partnerships and matchups."""
        return {
            'partnerships': dict(self.partnership_count),
            'opponents': dict(self.opponent_count)
        }
