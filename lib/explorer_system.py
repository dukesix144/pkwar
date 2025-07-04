"""Explorer tracking system for PKMUD with persistent storage"""

import sqlite3
import os
import time
from typing import List, Dict, Tuple, Optional
from datetime import datetime

class ExplorerSystem:
    """Manages room exploration tracking and rankings."""
    
    def __init__(self, db_path: str = "data/explorer.db"):
        self.db_path = db_path
        self.ensure_data_directory()
        self.init_database()
        
        # Cache for performance
        self.room_cache = {}  # player_name: set(room_names)
        self.last_room_cache = {}  # player_name: (room_name, timestamp)
    
    def ensure_data_directory(self):
        """Create data directory if it doesn't exist."""
        data_dir = os.path.dirname(self.db_path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
    
    def init_database(self):
        """Initialize the SQLite database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Explorer main table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS explorers (
                    player_name TEXT PRIMARY KEY,
                    total_rooms INTEGER DEFAULT 0,
                    last_new_room TEXT,
                    last_new_room_time REAL,
                    created_at REAL DEFAULT (julianday('now'))
                )
            ''')
            
            # Room exploration table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS room_exploration (
                    player_name TEXT,
                    room_name TEXT,
                    first_visited REAL DEFAULT (julianday('now')),
                    visit_count INTEGER DEFAULT 1,
                    PRIMARY KEY (player_name, room_name),
                    FOREIGN KEY (player_name) REFERENCES explorers(player_name)
                )
            ''')
            
            # Session tracking
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS exploration_sessions (
                    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT,
                    login_time REAL,
                    logout_time REAL,
                    rooms_explored INTEGER DEFAULT 0,
                    FOREIGN KEY (player_name) REFERENCES explorers(player_name)
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_room_player 
                ON room_exploration(player_name)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_explorer_rooms 
                ON explorers(total_rooms DESC)
            ''')
            
            conn.commit()
    
    def start_session(self, player_name: str) -> int:
        """Start a new exploration session for a player."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Ensure player exists in explorers table
            cursor.execute('''
                INSERT OR IGNORE INTO explorers (player_name) 
                VALUES (?)
            ''', (player_name,))
            
            # Create new session
            cursor.execute('''
                INSERT INTO exploration_sessions (player_name, login_time, rooms_explored)
                VALUES (?, julianday('now'), 0)
            ''', (player_name,))
            
            session_id = cursor.lastrowid
            conn.commit()
            
        # Load player's explored rooms into cache
        self.load_player_rooms(player_name)
        
        return session_id
    
    def end_session(self, player_name: str, session_id: int):
        """End an exploration session."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE exploration_sessions 
                SET logout_time = julianday('now')
                WHERE session_id = ? AND player_name = ?
            ''', (session_id, player_name))
            conn.commit()
        
        # Clear cache for player
        if player_name in self.room_cache:
            del self.room_cache[player_name]
        if player_name in self.last_room_cache:
            del self.last_room_cache[player_name]
    
    def load_player_rooms(self, player_name: str):
        """Load a player's explored rooms into cache."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT room_name FROM room_exploration
                WHERE player_name = ?
            ''', (player_name,))
            
            rooms = set(row[0] for row in cursor.fetchall())
            self.room_cache[player_name] = rooms
    
    def record_room_visit(self, player_name: str, room_name: str, session_id: int) -> bool:
        """
        Record a room visit. Returns True if it's a new room.
        """
        # Check cache first
        if player_name not in self.room_cache:
            self.load_player_rooms(player_name)
        
        is_new = room_name not in self.room_cache[player_name]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if is_new:
                # New room exploration
                cursor.execute('''
                    INSERT INTO room_exploration (player_name, room_name)
                    VALUES (?, ?)
                ''', (player_name, room_name))
                
                # Update explorer stats
                cursor.execute('''
                    UPDATE explorers 
                    SET total_rooms = total_rooms + 1,
                        last_new_room = ?,
                        last_new_room_time = julianday('now')
                    WHERE player_name = ?
                ''', (room_name, player_name))
                
                # Update session
                cursor.execute('''
                    UPDATE exploration_sessions
                    SET rooms_explored = rooms_explored + 1
                    WHERE session_id = ? AND player_name = ?
                ''', (session_id, player_name))
                
                # Update cache
                self.room_cache[player_name].add(room_name)
                self.last_room_cache[player_name] = (room_name, time.time())
            else:
                # Update visit count
                cursor.execute('''
                    UPDATE room_exploration 
                    SET visit_count = visit_count + 1
                    WHERE player_name = ? AND room_name = ?
                ''', (player_name, room_name))
            
            conn.commit()
        
        return is_new
    
    def get_player_stats(self, player_name: str) -> Dict:
        """Get exploration statistics for a player."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get basic stats
            cursor.execute('''
                SELECT total_rooms, last_new_room, last_new_room_time
                FROM explorers
                WHERE player_name = ?
            ''', (player_name,))
            
            row = cursor.fetchone()
            if not row:
                return {
                    'total_rooms': 0,
                    'last_new_room': None,
                    'last_new_room_time': None,
                    'session_rooms': 0,
                    'rank': 0,
                    'percentile': 0
                }
            
            total_rooms, last_room, last_time = row
            
            # Get current session rooms
            cursor.execute('''
                SELECT rooms_explored 
                FROM exploration_sessions
                WHERE player_name = ? AND logout_time IS NULL
                ORDER BY login_time DESC
                LIMIT 1
            ''', (player_name,))
            
            session_row = cursor.fetchone()
            session_rooms = session_row[0] if session_row else 0
            
            # Get rank
            cursor.execute('''
                SELECT COUNT(*) + 1
                FROM explorers
                WHERE total_rooms > ?
            ''', (total_rooms,))
            
            rank = cursor.fetchone()[0]
            
            # Get total number of explorers
            cursor.execute('SELECT COUNT(*) FROM explorers WHERE total_rooms > 0')
            total_explorers = cursor.fetchone()[0]
            
            percentile = ((total_explorers - rank + 1) / total_explorers * 100) if total_explorers > 0 else 0
            
            return {
                'total_rooms': total_rooms,
                'last_new_room': last_room,
                'last_new_room_time': last_time,
                'session_rooms': session_rooms,
                'rank': rank,
                'percentile': percentile
            }
    
    def get_top_explorers(self, limit: int = 20, include_offline: bool = True) -> List[Dict]:
        """Get top explorers by rooms explored."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT player_name, total_rooms, last_new_room_time
                FROM explorers
                WHERE total_rooms > 0
                ORDER BY total_rooms DESC
                LIMIT ?
            ''', (limit,))
            
            explorers = []
            for row in cursor.fetchall():
                player_name, total_rooms, last_time = row
                
                # Check if player is online (would need game_state reference)
                is_online = False  # This would be checked against active players
                
                explorers.append({
                    'name': player_name,
                    'rooms': total_rooms,
                    'last_exploration': last_time,
                    'online': is_online
                })
            
            return explorers
    
    def get_room_explorers(self, room_name: str) -> List[Tuple[str, float]]:
        """Get list of players who have explored a specific room."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT player_name, first_visited
                FROM room_exploration
                WHERE room_name = ?
                ORDER BY first_visited ASC
            ''', (room_name,))
            
            return cursor.fetchall()
    
    def get_unvisited_rooms(self, player_name: str, all_rooms: List[str]) -> List[str]:
        """Get list of rooms the player hasn't visited yet."""
        if player_name not in self.room_cache:
            self.load_player_rooms(player_name)
        
        visited = self.room_cache[player_name]
        return [room for room in all_rooms if room not in visited]
    
    def get_exploration_history(self, player_name: str, days: int = 30) -> List[Dict]:
        """Get exploration history for a player over the last N days."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT DATE(first_visited) as visit_date, COUNT(*) as rooms_found
                FROM room_exploration
                WHERE player_name = ? 
                AND first_visited >= julianday('now', '-' || ? || ' days')
                GROUP BY visit_date
                ORDER BY visit_date DESC
            ''', (player_name, days))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'date': row[0],
                    'rooms': row[1]
                })
            
            return history
    
    def get_area_completion(self, player_name: str, area_prefix: str) -> Dict:
        """Get completion percentage for a specific area."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Count total rooms in area
            cursor.execute('''
                SELECT COUNT(DISTINCT room_name)
                FROM room_exploration
                WHERE room_name LIKE ?
            ''', (f"{area_prefix}%",))
            
            total_in_area = cursor.fetchone()[0]
            
            # Count player's explored rooms in area
            cursor.execute('''
                SELECT COUNT(*)
                FROM room_exploration
                WHERE player_name = ? AND room_name LIKE ?
            ''', (player_name, f"{area_prefix}%",))
            
            explored_in_area = cursor.fetchone()[0]
            
            percentage = (explored_in_area / total_in_area * 100) if total_in_area > 0 else 0
            
            return {
                'area': area_prefix,
                'total_rooms': total_in_area,
                'explored_rooms': explored_in_area,
                'percentage': percentage
            }
    
    def award_exploration_bonus(self, player_name: str, milestone: int) -> bool:
        """Award bonus for reaching exploration milestones."""
        stats = self.get_player_stats(player_name)
        
        if stats['total_rooms'] >= milestone:
            # Could award XP, titles, or other bonuses here
            return True
        return False
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up old exploration sessions."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM exploration_sessions
                WHERE logout_time < julianday('now', '-' || ? || ' days')
            ''', (days,))
            conn.commit()
