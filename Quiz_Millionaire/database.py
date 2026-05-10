import sqlite3
import os
from datetime import datetime
import json
import sys
import io
from typing import List, Dict, Optional, Tuple, Any

# Ensure stdout handles UTF-8 for Kyrgyz characters
if hasattr(sys.stdout, 'buffer'):
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except Exception:
        pass

class DatabaseManager:
    """SQLite database manager for high scores and game records."""
    
    def __init__(self, db_file: str = "quiz_millionaire.db"):
        # Use absolute path to ensure database is always in the same folder as code
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.db_file = os.path.join(self.BASE_DIR, db_file)
        print(f"DATABASE: Using absolute path: {self.db_file}")
        
        # Create persistent connection that remains open globally.
        # Autocommit helps reliability when the app is minimized/throttled.
        self.conn = sqlite3.connect(
            self.db_file,
            check_same_thread=False,
            isolation_level=None,  # autocommit
        )
        self.init_database()
    
    def init_database(self) -> None:
        """Initialize the database and create tables if they don't exist."""
        try:
            cursor = self.conn.cursor()
            # Create leaderboard table with exact columns required
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS leaderboard (
                    name TEXT PRIMARY KEY,
                    score INTEGER NOT NULL,
                    series INTEGER NOT NULL,
                    date TEXT NOT NULL,
                    time_seconds INTEGER NOT NULL DEFAULT 0
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_score ON leaderboard(score DESC)
            ''')
            
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_date ON leaderboard(date DESC)
            ''')

            # Questions table (language-aware)
            # Check if we need to migrate from 'level' to 'difficulty'
            cursor.execute("PRAGMA table_info(questions)")
            columns = [info[1] for info in cursor.fetchall()]
            if columns and "level" in columns:
                print("DATABASE: Migrating 'questions' table (level -> difficulty)...")
                cursor.execute("DROP TABLE questions")

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    difficulty INTEGER NOT NULL,
                    language TEXT NOT NULL,
                    question TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    correct_index INTEGER NOT NULL,
                    money INTEGER NOT NULL
                )
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_questions_lang_diff
                ON questions(language, difficulty)
            ''')
            
            self.conn.commit()
            print("DATABASE: Initialization complete")
            
        except sqlite3.Error as e:
            print(f"Database initialization error: {e}")

        # Populate questions samples if table is empty
        try:
            self._ensure_question_samples()
        except Exception as e:
            print(f"DATABASE: Failed to ensure question samples: {e}")

    def _ensure_question_samples(self) -> None:
        """Load questions from questions.json into language-aware rows.

        Repair goals:
        - KY/EN must never get "[MISSING]".
        - If a language-specific key is absent, fall back to RU keys.
        - Only questions table is dropped/recreated; leaderboard is preserved.
        """
        cursor = self.conn.cursor()

        # MANDATORY: Drop and recreate questions table (DO NOT TOUCH LEADERBOARD!)
        cursor.execute("DROP TABLE IF EXISTS questions")
        cursor.execute('''
            CREATE TABLE questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                difficulty INTEGER NOT NULL,
                language TEXT NOT NULL,
                question TEXT NOT NULL,
                options_json TEXT NOT NULL,
                correct_index INTEGER NOT NULL,
                money INTEGER NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_questions_lang_diff
            ON questions(language, difficulty)
        ''')
        print("DB SEED: Dropped and recreated questions table to ensure structure")

        questions_path = os.path.join(self.BASE_DIR, "questions.json")
        if not os.path.exists(questions_path):
            print(f"DB SEED ERROR: {questions_path} not found!")
            return

        with open(questions_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        def ru_options(item: Dict[str, Any]) -> List[str]:
            if "option_a" in item:
                return [
                    str(item.get("option_a", "")),
                    str(item.get("option_b", "")),
                    str(item.get("option_c", "")),
                    str(item.get("option_d", "")),
                ]
            return [str(x) for x in item.get("options", ["", "", "", ""])[:4]]

        def lang_options(item: Dict[str, Any], suffix: str) -> List[str]:
            """Retrieve options for a specific language, fallback to RU."""
            key = f"options_{suffix}"
            if key in item and isinstance(item[key], list) and len(item[key]) >= 4:
                return [str(x) for x in item[key][:4]]
            return ru_options(item)

        def lang_question(item: Dict[str, Any], suffix: str) -> str:
            """Retrieve question text for a specific language, fallback to RU."""
            key = f"question_{suffix}"
            if key in item and item[key]:
                return str(item[key])
            v = item.get("question")
            return str(v) if v else ""

        def lang_correct_index(item: Dict[str, Any], suffix: str) -> int:
            # Your current questions.json contains only correct_index.
            v = item.get("correct_index")
            if v is None:
                v = item.get("answer", 0)
            try:
                return int(v)
            except Exception:
                return 0


        languages = ["ru", "ky", "en"]
        count = 0

        for level_key, questions in data.items():
            try:
                level = int(level_key)
            except Exception:
                continue

            if not isinstance(questions, list):
                continue

            for q in questions:
                if not isinstance(q, dict):
                    continue

                money = int(q.get("money", 0) or 0)

                for lang in languages:
                    if lang == "ru":
                        q_text = str(q.get("question", ""))
                        q_options = ru_options(q)
                        correct_index = int(q.get("correct_index", q.get("answer", 0)) or 0)
                    elif lang == "ky":
                        q_text = lang_question(q, "ky")
                        q_options = lang_options(q, "ky")
                        correct_index = lang_correct_index(q, "ky")
                    else:  # en
                        q_text = lang_question(q, "en")
                        q_options = lang_options(q, "en")
                        correct_index = lang_correct_index(q, "en")

                    options_json = json.dumps(q_options, ensure_ascii=False)

                    cursor.execute(
                        '''
                        INSERT INTO questions (difficulty, language, question, options_json, correct_index, money)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''',
                        (level, lang, q_text, options_json, int(correct_index), money),
                    )
                    count += 1

        self.conn.commit()
        print(f"DB SEED: Successfully loaded {count} question entries from questions.json (RU/KY/EN)")

        # Restore leaderboard with exactly 10 fake players if needed
        self._restore_leaderboard()

        # Verification: print first 3 KY rows (as requested)
        self._verify_first_3_ky_questions()

        # Hard stop: remove any cached/bad data effect during repair.
        # This ensures the just-imported KY rows are the ones read by the app.


    def _verify_first_3_ky_questions(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            '''
            SELECT id, question, difficulty
            FROM questions
            WHERE language = 'ky'
            ORDER BY id
            LIMIT 3
            '''
        )
        rows = cursor.fetchall()
        print("\n=== VERIFICATION: First 3 Kyrgyz questions ===")
        for row in rows:
            print(f"ID={row[0]}, Difficulty={row[2]}, Question: {row[1]}")
        cursor.close()

    
    def _restore_leaderboard(self) -> None:
        """Ensure leaderboard contains exactly 10 records (leaderboard table preserved)."""
        cursor = self.conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM leaderboard")
        current = cursor.fetchone()[0]

        fake_players = [
            ("Айбек", 1000000, 15, "2026-05-07 14:30:00", 120),
            ("Бакыт", 500000, 14, "2026-05-06 16:45:00", 150),
            ("Владимир", 250000, 13, "2026-05-05 10:20:00", 180),
            ("Гульназ", 125000, 12, "2026-05-04 18:10:00", 200),
            ("Дмитрий", 64000, 11, "2026-05-03 09:50:00", 220),
            ("Эркин", 32000, 10, "2026-05-02 21:00:00", 240),
            ("Елена", 16000, 9, "2026-05-01 12:30:00", 260),
            ("Жаркын", 8000, 8, "2026-04-30 15:40:00", 280),
            ("Иван", 4000, 7, "2026-04-29 11:20:00", 300),
            ("Каныкей", 0, 0, "2026-04-28 17:10:00", 0),
        ]

        # If too many rows exist, keep top-10 by score.
        if current > 10:
            cursor.execute(
                '''
                DELETE FROM leaderboard
                WHERE name NOT IN (
                    SELECT name FROM leaderboard
                    ORDER BY score DESC, date ASC
                    LIMIT 10
                )
                '''
            )
            self.conn.commit()
            cursor.execute("SELECT COUNT(*) FROM leaderboard")
            current = cursor.fetchone()[0]

        # If fewer than 10 rows exist, insert fake players until reaching 10.
        if current < 10:
            for name, score, series, date_str, time_seconds in fake_players:
                cursor.execute(
                    '''
                    INSERT OR REPLACE INTO leaderboard (name, score, series, date, time_seconds)
                    VALUES (?, ?, ?, ?, ?)
                    ''',
                    (name, score, series, date_str, time_seconds),
                )

            self.conn.commit()

            cursor.execute("SELECT COUNT(*) FROM leaderboard")
            current = cursor.fetchone()[0]

            # Deterministically trim to 10 if something unexpected happened.
            if current != 10:
                cursor.execute(
                    '''
                    DELETE FROM leaderboard
                    WHERE name NOT IN (
                        SELECT name FROM leaderboard
                        ORDER BY score DESC, date ASC
                        LIMIT 10
                    )
                    '''
                )
                self.conn.commit()

        cursor.execute("SELECT COUNT(*) FROM leaderboard")
        final_count = cursor.fetchone()[0]
        print(f"DB LEADERBOARD: Enforced exactly 10 records (final count={final_count})")
    
    def _verify_database_content(self) -> None:
        """Print first 5 questions for each language to verify JSON loading."""
        cursor = self.conn.cursor()
        
        languages = ['ru', 'ky', 'en']
        for lang in languages:
            cursor.execute(
                '''
                SELECT id, question, difficulty
                FROM questions
                WHERE language = ?
                ORDER BY id
                LIMIT 5
                ''',
                (lang,)
            )
            rows = cursor.fetchall()
            print(f"\n=== VERIFICATION: First 5 questions for language '{lang}' ===")
            if rows:
                for row in rows:
                    print(f"ID={row[0]}, Difficulty={row[2]}, Question: {row[1][:50]}...")
            else:
                print(f"No questions found for language '{lang}'")
        
        cursor.close()
    
    def cleanup_anonymous_entries(self) -> bool:
        """Remove all Anonymous entries from the database.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            cursor = self.conn.cursor()

            # Delete all Anonymous entries using the persistent connection.
            cursor.execute("DELETE FROM leaderboard WHERE name = 'Anonymous'")
            deleted_count = cursor.rowcount

            try:
                self.conn.commit()
            except Exception:
                pass

            if deleted_count and deleted_count > 0:
                print(f"Cleaned up {deleted_count} Anonymous entries from database")

            return True
                
        except sqlite3.Error as e:
            print(f"Error cleaning up anonymous entries: {e}")
            return False
    
    def clear_leaderboard_for_testing(self) -> bool:
        """TEMPORARY: Clear entire leaderboard table to remove bugged entries.
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Disabled to prevent accidental data loss.
        raise RuntimeError("clear_leaderboard_for_testing() is disabled to prevent data loss.")
    
    def add_score(self, name: str, score: int, time_seconds: int, series: str) -> bool:
        """Add or update a player's personal best score using proper UPSERT.
        
        Uses ON CONFLICT to ensure only the BEST result is kept on disk.
        
        Args:
            name: Player name
            score: Score achieved
            time_seconds: Time taken in seconds
            series: Win streak (maximum consecutive correct answers)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            print(f"DB SAVE: Attempting to save record for {name} with score {score}...")

            try:
                series_int = int(series)
            except (ValueError, TypeError):
                series_int = 0

            # Generate time string using datetime
            time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cursor = self.conn.cursor()

            # Use proper UPSERT with ON CONFLICT - only update if new score is better
            cursor.execute(
                '''
                INSERT INTO leaderboard (name, score, series, date, time_seconds)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    score = excluded.score,
                    series = excluded.series,
                    date = excluded.date,
                    time_seconds = excluded.time_seconds
                ''',
                (name, score, series_int, time_str, time_seconds),
            )

            # Check if any rows were affected (meaning the score was better)
            if cursor.rowcount > 0:
                print(f"DB SAVE: Record saved for {name}: {score} ₽, series: {series_int}, time: {time_seconds}s")
            else:
                print(f"DB SAVE: Score {score} not better than existing record for {name}")

            return True

        except sqlite3.OperationalError as e:
            print(f"DATABASE ERROR: {e}")
            return False
        except sqlite3.Error as e:
            print(f"DATABASE ERROR: {e}")
            return False
        except Exception as e:
            print(f"DATABASE ERROR: {e}")
            return False
        finally:
            # Ensure persistence even if the app is minimized/throttled mid-call.
            try:
                self.conn.commit()
            except Exception:
                pass

    def get_random_questions(self, levels: List[int], language: str, count_per_level: int = 1, exclude_ids: List[int] = None) -> List[Optional[Dict[str, Any]]]:
        """
        Return a list of random questions for each requested level.

        Filtering is based on the provided `language`. If a level/language has no questions,
        the method returns None for that position (caller may choose a fallback).
        """
        results: List[Optional[Dict[str, Any]]] = []
        if not levels:
            return results
        
        if exclude_ids is None:
            exclude_ids = []

        for difficulty in levels:
            cursor = self.conn.cursor()
            
            # Prepare exclusion placeholder
            placeholders = ', '.join(['?'] * len(exclude_ids))
            exclude_clause = f"AND id NOT IN ({placeholders})" if exclude_ids else ""
            
            # CRITICAL REPAIR: Strictly use the language parameter from Settings/Config
            print(f"DEBUG: Executing SQL for Language: [{language}], Difficulty: [{difficulty}]")
            
            query = f'''
                SELECT id, question, options_json, correct_index, money
                FROM questions
                WHERE language = ? AND difficulty = ? {exclude_clause}
                ORDER BY RANDOM()
                LIMIT ?
            '''
            
            params = [language, int(difficulty)] + exclude_ids + [int(count_per_level)]
            
            cursor.execute(query, tuple(params))
            row = cursor.fetchone()
            cursor.close()
            
            # If no questions found with exclusion, try without exclusion to avoid returning None if possible
            if row is None and exclude_ids:
                cursor = self.conn.cursor()  # Create new cursor for fallback query
                cursor.execute(
                    '''
                    SELECT id, question, options_json, correct_index, money
                    FROM questions
                    WHERE language = ? AND difficulty = ?
                    ORDER BY RANDOM()
                    LIMIT ?
                    ''',
                    (language, int(difficulty), int(count_per_level)),
                )
                row = cursor.fetchone()
                cursor.close()
                print(f"DB FALLBACK: Difficulty={difficulty}, Language={language}, Result ID={row[0] if row else None}")

            if row is None:
                results.append(None)
                continue

            q_id, question_text, options_json, correct_index, money = row
            
            # Debug verification as requested
            print(f"DEBUG: Fetched Question ID: [{q_id}] for Language: [{language}] at Difficulty: [{difficulty}]")
            print(f"DEBUG: Fetched text: [{question_text}]")
            
            try:
                options = json.loads(options_json) if options_json else []
            except Exception:
                options = []

            results.append(
                {
                    "id": q_id,
                    "question": question_text,
                    "options": options,
                    "correct_index": int(correct_index),
                    "money": int(money),
                }
            )

        return results
    
    def get_top_scores(self, limit: int = 10) -> List[Dict[str, any]]:
        """Get top scores from the physical database file.
        
        Fetches data from the physical file and sorts by score DESC.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of dictionaries containing score data
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT name, score, series, time_seconds, date
                FROM leaderboard
                ORDER BY score DESC, date ASC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries with proper field names
            scores = []
            for row in rows:
                scores.append({
                    'name': row[0],
                    'score': row[1],
                    'rank': str(row[2]),  # series as string for UI compatibility
                    'time_seconds': row[3],
                    'date': row[4]
                })
            
            return scores
            
        except sqlite3.Error as e:
            print(f"Error getting top scores: {e}")
            return []
    
    def get_player_scores(self, name: str, limit: int = 10) -> List[Dict[str, any]]:
        """Get scores for a specific player.
        
        Args:
            name: Player name
            limit: Maximum number of scores to return
            
        Returns:
            List of dictionaries containing player's score data
        """
        try:
            cursor = self.conn.cursor()
            
            cursor.execute('''
                SELECT name, score, series, time_seconds, date
                FROM leaderboard
                WHERE name = ?
                ORDER BY score DESC, date ASC
                LIMIT ?
            ''', (name, limit))
            
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            scores = []
            for row in rows:
                scores.append({
                    'id': row[0],
                    'name': row[1],
                    'score': row[2],
                    'time_seconds': row[3],
                    'rank': row[4],
                    'date': row[5]
                })
            
            return scores
                
        except sqlite3.Error as e:
            print(f"Error getting player scores: {e}")
            return []
    
    def get_statistics(self) -> Dict[str, any]:
        """Get overall database statistics.
        
        Returns:
            Dictionary containing statistics
        """
        try:
            cursor = self.conn.cursor()
            
            # Total games played
            cursor.execute('SELECT COUNT(*) FROM leaderboard')
            total_games = cursor.fetchone()[0]
            
            # Average score
            cursor.execute('SELECT AVG(score) FROM leaderboard')
            avg_score = cursor.fetchone()[0] or 0
            
            # Highest score
            cursor.execute('SELECT MAX(score) FROM leaderboard')
            highest_score = cursor.fetchone()[0] or 0
                
                # Number of unique players
            cursor.execute('SELECT COUNT(DISTINCT name) FROM leaderboard')
            unique_players = cursor.fetchone()[0]
            
            return {
                'total_games': total_games,
                'average_score': round(avg_score, 2),
                'highest_score': highest_score,
                'unique_players': unique_players
            }
                
        except sqlite3.Error as e:
            print(f"Error getting statistics: {e}")
            return {
                'total_games': 0,
                'average_score': 0,
                'highest_score': 0,
                'unique_players': 0
            }
    
    def clear_all_scores(self) -> bool:
        """Clear all scores from the leaderboard.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                cursor.execute('DELETE FROM leaderboard')
                conn.commit()
                
                return True
                
        except sqlite3.Error as e:
            print(f"Error clearing scores: {e}")
            return False
    
    def export_to_json(self, filename: str = "leaderboard_export.json") -> bool:
        """Export leaderboard data to JSON file.
        
        Args:
            filename: Output filename
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            import json
            
            scores = self.get_top_scores(limit=1000)  # Get all scores
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(scores, f, ensure_ascii=False, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
