"""
Match Storage System for Badminton Matchups

This module handles persistence of match history using JSON files.
"""

import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class MatchStorage:
    def __init__(self, data_dir: str = "data"):
        """
        Initialize the match storage system.
        
        Args:
            data_dir: Directory to store match data files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.matches_file = self.data_dir / "matches.json"
        self.sessions_file = self.data_dir / "sessions.json"
        
    def _load_json(self, file_path: Path) -> List[Dict]:
        """Load data from a JSON file."""
        if not file_path.exists():
            return []
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    
    def _save_json(self, file_path: Path, data: List[Dict]):
        """Save data to a JSON file."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def save_match(self, match_data: Dict) -> str:
        """
        Save a match to the history.
        
        Args:
            match_data: Dictionary containing match information
            
        Returns:
            Match ID
        """
        matches = self._load_json(self.matches_file)
        
        # Generate match ID
        match_id = f"match_{len(matches) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Add metadata
        match_record = {
            'match_id': match_id,
            'timestamp': datetime.now().isoformat(),
            **match_data
        }
        
        matches.append(match_record)
        self._save_json(self.matches_file, matches)
        
        return match_id
    
    def get_all_matches(self) -> List[Dict]:
        """
        Retrieve all matches from history.
        
        Returns:
            List of match dictionaries
        """
        return self._load_json(self.matches_file)
    
    def get_matches_by_player(self, player_name: str) -> List[Dict]:
        """
        Get all matches involving a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            List of matches involving the player
        """
        all_matches = self.get_all_matches()
        player_matches = []
        
        for match in all_matches:
            team1 = match.get('team1', [])
            team2 = match.get('team2', [])
            if player_name in team1 or player_name in team2:
                player_matches.append(match)
        
        return player_matches
    
    def get_recent_matches(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent matches.
        
        Args:
            limit: Maximum number of matches to return
            
        Returns:
            List of recent matches
        """
        matches = self.get_all_matches()
        return matches[-limit:] if matches else []
    
    def save_session(self, session_data: Dict) -> str:
        """
        Save a complete session.
        
        Args:
            session_data: Dictionary containing session information
            
        Returns:
            Session ID
        """
        sessions = self._load_json(self.sessions_file)
        
        # Generate session ID
        session_id = f"session_{len(sessions) + 1}_{datetime.now().strftime('%Y%m%d')}"
        
        # Add metadata
        session_record = {
            'session_id': session_id,
            'date': datetime.now().isoformat(),
            **session_data
        }
        
        sessions.append(session_record)
        self._save_json(self.sessions_file, sessions)
        
        return session_id
    
    def get_all_sessions(self) -> List[Dict]:
        """
        Retrieve all sessions from history.
        
        Returns:
            List of session dictionaries
        """
        return self._load_json(self.sessions_file)
    
    def get_player_stats(self, player_name: str) -> Dict:
        """
        Calculate statistics for a specific player.
        
        Args:
            player_name: Name of the player
            
        Returns:
            Dictionary with player statistics
        """
        matches = self.get_matches_by_player(player_name)
        
        stats = {
            'total_matches': len(matches),
            'wins': 0,
            'losses': 0,
            'total_earnings': 0.0,
            'partners': set(),
            'opponents': set()
        }
        
        for match in matches:
            team1 = match.get('team1', [])
            team2 = match.get('team2', [])
            team1_score = match.get('team1_score')
            team2_score = match.get('team2_score')
            
            # Determine if player was on team1 or team2
            on_team1 = player_name in team1
            
            # Track partners and opponents
            if on_team1:
                stats['partners'].update([p for p in team1 if p != player_name])
                stats['opponents'].update(team2)
            else:
                stats['partners'].update([p for p in team2 if p != player_name])
                stats['opponents'].update(team1)
            
            # Track wins/losses if scores are available
            if team1_score is not None and team2_score is not None:
                if on_team1:
                    if team1_score > team2_score:
                        stats['wins'] += 1
                    else:
                        stats['losses'] += 1
                else:
                    if team2_score > team1_score:
                        stats['wins'] += 1
                    else:
                        stats['losses'] += 1
            
            # Track earnings if available
            if 'game_value' in match:
                value = match['game_value']
                if team1_score is not None and team2_score is not None:
                    won_match = (on_team1 and team1_score > team2_score) or \
                               (not on_team1 and team2_score > team1_score)
                    if won_match:
                        stats['total_earnings'] += value / 2  # Split with partner
        
        # Convert sets to lists for JSON serialization
        stats['partners'] = list(stats['partners'])
        stats['opponents'] = list(stats['opponents'])
        stats['total_earnings'] = round(stats['total_earnings'], 2)
        
        if stats['total_matches'] > 0:
            stats['win_rate'] = round(stats['wins'] / stats['total_matches'] * 100, 1)
        else:
            stats['win_rate'] = 0.0
        
        return stats
    
    def clear_history(self):
        """Clear all match and session history."""
        if self.matches_file.exists():
            self.matches_file.unlink()
        if self.sessions_file.exists():
            self.sessions_file.unlink()
    
    def export_to_csv(self, output_file: str):
        """
        Export match history to CSV format.
        
        Args:
            output_file: Path to output CSV file
        """
        import csv
        
        matches = self.get_all_matches()
        if not matches:
            return
        
        with open(output_file, 'w', newline='') as f:
            fieldnames = ['match_id', 'timestamp', 'team1', 'team2', 
                         'team1_score', 'team2_score', 'game_value']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            writer.writeheader()
            for match in matches:
                row = {
                    'match_id': match.get('match_id', ''),
                    'timestamp': match.get('timestamp', ''),
                    'team1': ' & '.join(match.get('team1', [])),
                    'team2': ' & '.join(match.get('team2', [])),
                    'team1_score': match.get('team1_score', ''),
                    'team2_score': match.get('team2_score', ''),
                    'game_value': match.get('game_value', '')
                }
                writer.writerow(row)
