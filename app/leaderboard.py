import json
import os
from datetime import datetime
from collections import defaultdict

class LeaderboardManager:
    def __init__(self, filename="leaderboard.json"):
        self.filename = filename
        self.scores = self._load_scores()

    def _load_scores(self):
        """Load scores from file"""
        if not os.path.exists(self.filename):
            return []
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert date strings back to datetime objects
                for score in data:
                    if isinstance(score.get('date'), str):
                        score['date'] = datetime.fromisoformat(score['date'])
                return data
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            return []

    def _save_scores(self):
        """Save scores to file"""
        try:
            # Convert datetime objects to strings for JSON serialization
            data_to_save = []
            for score in self.scores:
                score_copy = score.copy()
                if isinstance(score_copy.get('date'), datetime):
                    score_copy['date'] = score_copy['date'].isoformat()
                data_to_save.append(score_copy)
            
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data_to_save, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"Error saving leaderboard: {e}")

    def add_score(self, player_name, score, time_taken, moves, difficulty):
        """Add a new score to the leaderboard"""
        score_entry = {
            'player_name': player_name,
            'score': score,
            'time': time_taken,
            'moves': moves,
            'difficulty': difficulty,
            'date': datetime.now()
        }
        
        self.scores.append(score_entry)
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 100 scores to prevent file from growing too large
        self.scores = self.scores[:100]
        
        self._save_scores()

    def get_top_scores(self, difficulty=None, limit=50):
        """Get top scores, optionally filtered by difficulty"""
        filtered_scores = self.scores
        
        if difficulty:
            filtered_scores = [s for s in self.scores if s['difficulty'] == difficulty]
        
        return filtered_scores[:limit]

    def get_player_best(self, player_name, difficulty=None):
        """Get player's best score"""
        player_scores = [s for s in self.scores if s['player_name'] == player_name]
        
        if difficulty:
            player_scores = [s for s in player_scores if s['difficulty'] == difficulty]
        
        return player_scores[0] if player_scores else None

    def get_statistics(self):
        """Get general statistics"""
        if not self.scores:
            return None

        total_games = len(self.scores)
        total_players = len(set(score['player_name'] for score in self.scores))
        avg_score = sum(score['score'] for score in self.scores) / total_games
        avg_time = sum(score['time'] for score in self.scores) / total_games
        avg_moves = sum(score['moves'] for score in self.scores) / total_games

        # Difficulty breakdown
        difficulty_breakdown = defaultdict(int)
        for score in self.scores:
            difficulty_breakdown[score['difficulty']] += 1

        # Top players by average score
        player_scores = defaultdict(list)
        for score in self.scores:
            player_scores[score['player_name']].append(score['score'])
        
        top_players = []
        for player, scores in player_scores.items():
            avg_player_score = sum(scores) / len(scores)
            top_players.append((player, int(avg_player_score)))
        
        top_players.sort(key=lambda x: x[1], reverse=True)

        return {
            'total_games': total_games,
            'total_players': total_players,
            'avg_score': avg_score,
            'avg_time': avg_time,
            'avg_moves': avg_moves,
            'difficulty_breakdown': dict(difficulty_breakdown),
            'top_players': top_players
        }
