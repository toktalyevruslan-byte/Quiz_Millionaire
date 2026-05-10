import json
import os
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, stats_file: str = "records.json", profile_file: str = "profile.json", settings_file: str = "settings.json"):
        self.stats_file = stats_file
        self.profile_file = profile_file
        self.settings_file = settings_file
        
        # Global integers for stats tracking
        self.total_questions = 0
        self.correct_answers = 0
        
        # Load stats immediately from profile.json
        self._load_stats_from_json()
    
    def _load_stats_from_json(self) -> None:
        """Load stats from profile.json into global variables."""
        try:
            profile = self.get_profile() or {}
            self.total_questions = int(profile.get("total_questions_encountered", 0))
            self.correct_answers = int(profile.get("total_correct_answers", 0))
            print(f"STATS LOADED: Total={self.total_questions}, Correct={self.correct_answers}")
        except Exception as e:
            print(f"ERROR loading stats: {e}")
            self.total_questions = 0
            self.correct_answers = 0
    
    def update_stats(self, is_correct: bool) -> None:
        """Update global stats and save immediately to JSON."""
        try:
            # Increment counters
            self.total_questions += 1
            if is_correct:
                self.correct_answers += 1
            
            print(f"STATS UPDATE: Total={self.total_questions}, Correct={self.correct_answers}")
            
            # Save immediately to JSON
            self.save_to_json()
            
        except Exception as e:
            print(f"ERROR updating stats: {e}")
    
    def save_to_json(self) -> None:
        """Save global stats to profile.json immediately."""
        try:
            profile = self.get_profile() or {}
            
            # STRICT INTEGER CONVERSION - Force these variables to be integers
            self.total_questions = int(self.total_questions)
            self.correct_answers = int(self.correct_answers)
            
            profile["total_questions_encountered"] = self.total_questions
            profile["total_correct_answers"] = self.correct_answers
            
            # Also ensure other numeric fields are integers
            if "total_games" in profile:
                profile["total_games"] = int(profile["total_games"])
            if "total_win" in profile:
                profile["total_win"] = int(profile["total_win"])
            if "max_score" in profile:
                profile["max_score"] = int(profile["max_score"])
            if "game_iq" in profile:
                profile["game_iq"] = int(profile["game_iq"])
            if "total_games_played" in profile:
                profile["total_games_played"] = int(profile["total_games_played"])
            
            # Handle sets that are not JSON serializable - convert ALL sets to lists
            for key, value in profile.items():
                if isinstance(value, set):
                    profile[key] = list(value)
                elif isinstance(value, dict):
                    # Handle nested dictionaries with sets
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, set):
                            value[sub_key] = list(sub_value)
            
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            
            print(f"STATS SAVED: SUCCESS - Total={self.total_questions}, Correct={self.correct_answers}")
            
        except Exception as e:
            print(f"ERROR saving stats to JSON: {e}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            print(f"DEBUG: total_questions type: {type(self.total_questions)}")
            print(f"DEBUG: correct_answers type: {type(self.correct_answers)}")
            import traceback
            traceback.print_exc()

    # ---------- Методы для званий ----------

    def _default_achievements(self) -> Dict[str, bool]:
        return {
            "first_success": False,
            "fireproof": False,
            "iron_nerves": False,
            "peoples_voice": False,
            "super_intuition": False,
            "smart_exit": False,
            "book_worm": False,
            "survival_master": False,
            "genius_iq": False,
            "legend": False,
        }

    def get_title(self, iq: float, max_score: int) -> str:
        if max_score >= 1000000:
            return "Миллионер"
        elif iq < 85:
            return "Новичок"
        elif iq < 105:
            return "Студент"
        elif iq < 125:
            return "Интеллектуал"
        elif iq < 150:
            return "Эрудит"
        elif iq < 180:
            return "Магистр"
        else:
            return "Академик"

    # ---------- Методы для достижений ----------

    def get_achievements(self) -> Dict[str, bool]:
        profile = self.get_profile() or {}
        achievements = profile.get("achievements", {})
        default = self._default_achievements()
        for key, value in default.items():
            achievements.setdefault(key, value)
        return achievements

    def update_achievements(self, unlocked: Dict[str, bool]) -> None:
        profile = self.get_profile() or {}
        profile.setdefault("achievements", {})
        achievements = profile["achievements"]
        for key, value in self._default_achievements().items():
            achievements.setdefault(key, value)

        for key, value in unlocked.items():
            if value and key in achievements:
                achievements[key] = True

        profile["achievements"] = achievements
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

    # ---------- Методы для Рекордов ----------

    def save_score(self, name: str, money: int) -> None:
        scores = self._load_scores()
        scores.append({"name": name, "score": money})
        # Сортировка по score убыванию
        scores.sort(key=lambda x: x["score"], reverse=True)
        # Ограничить топ-10
        scores = scores[:10]
        self._save_scores(scores)

    def get_top_scores(self) -> List[Dict[str, any]]:
        return self._load_scores()

    def get_player_records(self, name: str) -> List[Dict[str, any]]:
        return [record for record in self._load_scores() if record.get("name") == name]

    def _load_scores(self) -> List[Dict[str, any]]:
        if os.path.exists(self.stats_file):
            try:
                with open(self.stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return []
        return []

    def _save_scores(self, scores: List[Dict[str, any]]) -> None:
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(scores, f, ensure_ascii=False, indent=4)

    # ---------- Методы для Профиля ----------

    def get_profile(self) -> Optional[Dict[str, any]]:
        if os.path.exists(self.profile_file):
            try:
                with open(self.profile_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return None
        return None

    def update_profile(self, money: int) -> None:
        profile = self.get_profile() or {}

        # Normalize structure (on case of old format)
        profile.setdefault("name", "")
        profile.setdefault("total_games", 0)
        profile.setdefault("total_win", 0)
        profile.setdefault("max_score", 0)
        profile.setdefault("total_questions_answered", 0)
        profile.setdefault("total_correct_answers", 0)
        profile.setdefault("game_iq", 100)  # Start at 100
        profile.setdefault("total_games_played", 0)
        profile.setdefault("achievements", {})
        for key, value in self._default_achievements().items():
            profile["achievements"].setdefault(key, value)
        
        # Rank system tracking
        profile.setdefault("current_rank", "Новичок")
        profile.setdefault("consecutive_10th_questions", 0)
        profile.setdefault("total_capital", 0)
        profile.setdefault("categories_unlocked", set())
        profile.setdefault("full_game_sessions", 0)

        profile["total_games"] = int(profile["total_games"]) + 1
        profile["total_games_played"] = int(profile["total_games_played"]) + 1
        profile["total_win"] = int(profile["total_win"]) + int(money)
        profile["max_score"] = max(int(profile["max_score"]), int(money))
        
        # Update total capital for rank tracking
        profile["total_capital"] = int(profile.get("total_capital", 0)) + int(money)

        self.force_save_to_disk(profile)

    def force_save_to_disk(self, profile: dict) -> bool:
        """Force immediate disk write of profile data with debug logging."""
        try:
            # STRICT INTEGER CONVERSION - Force these variables to be integers
            if "total_questions_encountered" in profile:
                profile["total_questions_encountered"] = int(profile["total_questions_encountered"])
            if "total_correct_answers" in profile:
                profile["total_correct_answers"] = int(profile["total_correct_answers"])
            
            # Also ensure other numeric fields are integers
            if "total_games" in profile:
                profile["total_games"] = int(profile["total_games"])
            if "total_win" in profile:
                profile["total_win"] = int(profile["total_win"])
            if "max_score" in profile:
                profile["max_score"] = int(profile["max_score"])
            if "game_iq" in profile:
                profile["game_iq"] = int(profile["game_iq"])
            if "total_games_played" in profile:
                profile["total_games_played"] = int(profile["total_games_played"])
            
            # Handle sets that are not JSON serializable - convert ALL sets to lists
            for key, value in profile.items():
                if isinstance(value, set):
                    profile[key] = list(value)
                elif isinstance(value, dict):
                    # Handle nested dictionaries with sets
                    for sub_key, sub_value in value.items():
                        if isinstance(sub_value, set):
                            value[sub_key] = list(sub_value)
            
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            
            total_questions = profile.get("total_questions_encountered", 0)
            correct_answers = profile.get("total_correct_answers", 0)
            print(f"Profile saved successfully - Total: {total_questions}, Correct: {correct_answers}")
            return True
        except Exception as e:
            print(f"ERROR: Failed to save profile to disk: {e}")
            print(f"DEBUG: Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False

    def update_correct_answers(self, correct: bool, level: int, time_taken: int = 30) -> None:
        """Update statistics immediately after every answer."""
        profile = self.get_profile() or {}
        profile.setdefault("total_questions_encountered", 0)
        profile.setdefault("total_correct_answers", 0)
        profile.setdefault("game_iq", 100)  # Start at 100
        profile.setdefault("total_games_played", 0)
        profile.setdefault("achievements", {})
        for key, value in self._default_achievements().items():
            profile["achievements"].setdefault(key, value)

        # Track every question encountered
        profile["total_questions_encountered"] += 1
        
        if correct:
            profile["total_correct_answers"] += 1
            
            # Game IQ calculation for correct answers
            iq_change = 2  # Base +2 points for correct answer
            
            # Fast answer bonus (within 10 seconds)
            if time_taken <= 10:
                iq_change += 3  # Additional bonus for fast answers
            
            # Safety net bonus (levels 5 and 10)
            if level == 5 or level == 10:  # Safety net levels (0-indexed: 4 and 9)
                iq_change += 10  # Safety net bonus
            
            profile["game_iq"] += iq_change
        else:
            # Penalty for incorrect answers
            profile["game_iq"] -= 5
        
        # Cap Game IQ at maximum of 200 and minimum of 0
        profile["game_iq"] = max(0, min(200, profile["game_iq"]))

        # FORCED DISK WRITE: Update profile.json after every answer
        self.force_save_to_disk(profile)

    def create_profile(self, name: str) -> None:
        profile = {
            "name": name,
            "total_games": 0,
            "total_win": 0,
            "max_score": 0,
            "total_questions_answered": 0,
            "total_correct_answers": 0,
            "total_games_played": 0,
            "game_iq": 100,  # Start at 100
            "achievements": self._default_achievements(),
        }
        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

    def clear_all_data(self) -> None:
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)
        if os.path.exists(self.profile_file):
            os.remove(self.profile_file)
        if os.path.exists(self.settings_file):
            os.remove(self.settings_file)

    # ---------- Методы для Настроек ----------

    def get_settings(self) -> Dict[str, any]:
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def save_settings(self, settings: Dict[str, any]) -> None:
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

    # ---------- Методы для достижений ----------
    
    def get_achievements_data(self) -> Dict[str, any]:
        """Get all achievements data from achievements.json."""
        if os.path.exists("achievements.json"):
            try:
                with open("achievements.json", 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return self._default_achievements_data()
        return self._default_achievements_data()
    
    def save_achievements_data(self, achievements_data: Dict[str, any]) -> None:
        """Save achievements data to achievements.json."""
        with open("achievements.json", 'w', encoding='utf-8') as f:
            json.dump(achievements_data, f, ensure_ascii=False, indent=4)
    
    def _default_achievements_data(self) -> Dict[str, any]:
        """Default achievements data structure."""
        return {
            "achievements": {
                "first_step": {
                    "id": "first_step",
                    "title": "Первый шаг",
                    "description": "Дать первый правильный ответ",
                    "category": "Путь к богатству",
                    "is_unlocked": False
                },
                "first_million": {
                    "id": "first_million",
                    "title": "Первый миллион",
                    "description": "Впервые выиграть 1,000,000 за одну игру",
                    "category": "Путь к богатству",
                    "is_unlocked": False
                },
                "cold_blood": {
                    "id": "cold_blood",
                    "title": "Хладнокровие",
                    "description": "Ответить на 10 вопросов, тратя менее 10 секунд на каждый",
                    "category": "Путь к богатству",
                    "is_unlocked": False
                },
                "jackpot": {
                    "id": "jackpot",
                    "title": "Джекпот!",
                    "description": "Ответить на финальный, 15-й вопрос",
                    "category": "Путь к богатству",
                    "is_unlocked": False
                },
                "veteran": {
                    "id": "veteran",
                    "title": "Ветеран",
                    "description": "Ответить на 500 вопросов за всё время",
                    "category": "Путь к богатству",
                    "is_unlocked": False
                },
                "risky_guy": {
                    "id": "risky_guy",
                    "title": "Рисковый парень",
                    "description": "Дойти до 10-го вопроса, не потратив ни одной подсказки",
                    "category": "Работа с подсказками",
                    "is_unlocked": False
                },
                "voice_of_people": {
                    "id": "voice_of_people",
                    "title": "Глас народа",
                    "description": "Победить, выбрав вариант «Помощь зала»",
                    "category": "Работа с подсказками",
                    "is_unlocked": False
                },
                "friend_in_need": {
                    "id": "friend_in_need",
                    "title": "Друг в беде",
                    "description": "Использовать «Звонок другу» на вопросе выше 10-го и ответить верно",
                    "category": "Работа с подсказками",
                    "is_unlocked": False
                },
                "va_bank": {
                    "id": "va_bank",
                    "title": "Ва-банк",
                    "description": "Использовать все три подсказки на одном и том же вопросе",
                    "category": "Работа с подсказками",
                    "is_unlocked": False
                },
                "own_mind": {
                    "id": "own_mind",
                    "title": "Своим умом",
                    "description": "Пройти всю игру до конца, не использовав ни одной подсказки",
                    "category": "Работа с подсказками",
                    "is_unlocked": False
                },
                "on_the_edge": {
                    "id": "on_the_edge",
                    "title": "На грани",
                    "description": "Дать верный ответ, когда на таймере осталось меньше 2 секунд",
                    "category": "Сложные ситуации",
                    "is_unlocked": False
                },
                "bird_in_hand": {
                    "id": "bird_in_hand",
                    "title": "Синица в руках",
                    "description": "Забрать деньги (кнопка «Take Money») на вопросе выше 12-го",
                    "category": "Сложные ситуации",
                    "is_unlocked": False
                },
                "bitter_experience": {
                    "id": "bitter_experience",
                    "title": "Горький опыт",
                    "description": "Проиграть на финальном 15-м вопросе",
                    "category": "Сложные ситуации",
                    "is_unlocked": False
                },
                "sprinter": {
                    "id": "sprinter",
                    "title": "Спринтер",
                    "description": "Пройти всю игру (все 15 вопросов) быстрее чем за 2 минуты",
                    "category": "Сложные ситуации",
                    "is_unlocked": False
                },
                "intellectual_series": {
                    "id": "intellectual_series",
                    "title": "Интеллектуальная серия",
                    "description": "Три игры подряд без единой ошибки (до первой несгораемой суммы или до конца)",
                    "category": "Сложные ситуации",
                    "is_unlocked": False
                },
                "magnate": {
                    "id": "magnate",
                    "title": "Магнат",
                    "description": "Накопить общий капитал в 1 000 000 000 (суммарно за все игры)",
                    "category": "Особые заслуги",
                    "is_unlocked": False
                },
                "cautious_strategist": {
                    "id": "cautious_strategist",
                    "title": "Осторожный стратег",
                    "description": "Забрать деньги 20 раз за всю карьеру",
                    "category": "Особые заслуги",
                    "is_unlocked": False
                },
                "history_expert": {
                    "id": "history_expert",
                    "title": "Знаток истории",
                    "description": "Дать 50 правильных ответов в категории «История»",
                    "category": "Особые заслуги",
                    "is_unlocked": False
                },
                "jack_of_all_trades": {
                    "id": "jack_of_all_trades",
                    "title": "Мастер на все руки",
                    "description": "Правильно ответить на вопросы из 10 разных областей знаний",
                    "category": "Особые заслуги",
                    "is_unlocked": False
                },
                "club_legend": {
                    "id": "club_legend",
                    "title": "Легенда клуба",
                    "description": "Собрать остальные 19 достижений",
                    "category": "Особые заслуги",
                    "is_unlocked": False
                }
            },
            "session_stats": {
                "current_session_correct": 0,
                "current_session_hints": {
                    "50_50": False,
                    "audience": False,
                    "call_friend": False
                },
                "current_question_hints": [],
                "fast_answers_count": 0,
                "game_start_time": 0,
                "consecutive_games": 0,
                "take_money_count": 0,
                "category_answers": {},
                "total_capital": 0
            }
        }
    
    def unlock_achievement(self, achievement_id: str) -> None:
        """Unlock an achievement and save to file."""
        achievements_data = self.get_achievements_data()
        if achievement_id in achievements_data["achievements"]:
            achievements_data["achievements"][achievement_id]["is_unlocked"] = True
            self.save_achievements_data(achievements_data)
    
    def is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if achievement is unlocked."""
        achievements_data = self.get_achievements_data()
        return achievements_data["achievements"].get(achievement_id, {}).get("is_unlocked", False)
    
    def update_session_stats(self, **kwargs) -> None:
        """Update session statistics for achievement tracking."""
        achievements_data = self.get_achievements_data()
        session_stats = achievements_data["session_stats"]
        
        for key, value in kwargs.items():
            if key in session_stats:
                session_stats[key] = value
        
        self.save_achievements_data(achievements_data)
    
    def get_session_stats(self) -> Dict[str, any]:
        """Get current session statistics."""
        achievements_data = self.get_achievements_data()
        return achievements_data["session_stats"]

    # ---------- Методы для Ранговой Системы ----------
    
    def get_rank_data(self) -> Dict[str, any]:
        """Get rank hierarchy and requirements."""
        return {
            "Новичок": {
                "level": 1,
                "description": "Начальный уровень",
                "requirements": "Регистрация в игре",
                "icon": "🎯"
            },
            "Любитель": {
                "level": 2,
                "description": "Опытный игрок",
                "requirements": "50 правильных ответов",
                "icon": "⭐"
            },
            "Эрудит": {
                "level": 3,
                "description": "Знаток trivia",
                "requirements": "5,000,000 накопленного капитала",
                "icon": "📚"
            },
            "Знаток": {
                "level": 4,
                "description": "Эксперт игры",
                "requirements": "10 полных игровых сессий",
                "icon": "🎓"
            },
            "Аналитик": {
                "level": 5,
                "description": "Стратегический игрок",
                "requirements": "10-й вопрос в 5 играх подряд",
                "icon": "🔍"
            },
            "Миллионер": {
                "level": 6,
                "description": "Победитель миллиона",
                "requirements": "15-й вопрос пройден хотя бы раз",
                "icon": "💰"
            },
            "Магистр": {
                "level": 7,
                "description": "Мастер игры",
                "requirements": "100,000,000 накопленных выигрышей",
                "icon": "👑"
            },
            "Оракул": {
                "level": 8,
                "description": "Легендарный игрок",
                "requirements": "Все категории и 20 достижений",
                "icon": "🔮"
            }
        }
    
    def get_current_rank(self) -> str:
        """Get player's current rank."""
        profile = self.get_profile() or {}
        return profile.get("current_rank", "Новичок")
    
    def check_rank_up(self, current_level: int = None, game_completed: bool = False) -> str:
        """Check and update player rank based on achievements and stats."""
        profile = self.get_profile() or {}
        current_rank = profile.get("current_rank", "Новичок")
        rank_data = self.get_rank_data()
        
        # Get current stats
        total_questions = profile.get("total_correct_answers", 0)
        total_capital = profile.get("total_capital", 0)
        total_games = profile.get("total_games_played", 0)
        max_score = profile.get("max_score", 0)
        
        # Track consecutive 10th questions
        if current_level == 10:
            consecutive_10th = profile.get("consecutive_10th_questions", 0) + 1
            profile["consecutive_10th_questions"] = consecutive_10th
        elif current_level and current_level < 10:
            profile["consecutive_10th_questions"] = 0
        
        # Track full game sessions
        if game_completed:
            profile["full_game_sessions"] = profile.get("full_game_sessions", 0) + 1
        
        # Check rank requirements in order
        new_rank = current_rank
        
        # Check Любитель - 50 correct answers
        if total_questions >= 50 and rank_data["Любитель"]["level"] > rank_data[current_rank]["level"]:
            new_rank = "Любитель"
        
        # Check Эрудит - 5,000,000 total capital
        if total_capital >= 5000000 and rank_data["Эрудит"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Эрудит"
        
        # Check Знаток - 10 full game sessions
        if profile.get("full_game_sessions", 0) >= 10 and rank_data["Знаток"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Знаток"
        
        # Check Аналитик - 10th question in 5 consecutive games
        if profile.get("consecutive_10th_questions", 0) >= 5 and rank_data["Аналитик"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Аналитик"
        
        # Check Миллионер - reached 15th question
        if max_score >= 1000000 and rank_data["Миллионер"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Миллионер"
        
        # Check Магистр - 100,000,000 total winnings
        if total_capital >= 100000000 and rank_data["Магистр"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Магистр"
        
        # Check Оракул - all achievements and categories
        achievements_data = self.get_achievements_data()
        unlocked_achievements = sum(1 for achievement in achievements_data["achievements"].values() 
                                  if achievement.get("is_unlocked", False))
        all_categories_unlocked = True  # Simplified - assume all categories available
        
        if unlocked_achievements >= 20 and all_categories_unlocked and rank_data["Оракул"]["level"] > rank_data[new_rank]["level"]:
            new_rank = "Оракул"
        
        # Update rank if changed
        if new_rank != current_rank:
            profile["current_rank"] = new_rank
            with open(self.profile_file, 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
        
        return new_rank

    # ---------- Методы для статистики ----------

    def get_answer_accuracy(self) -> float:
        """Calculate answer accuracy as percentage."""
        profile = self.get_profile() or {}
        total_questions = profile.get("total_questions_encountered", 0)
        correct_answers = profile.get("total_correct_answers", 0)
        
        if total_questions == 0:
            return 0.0  # Handle division by zero
        
        accuracy = (correct_answers / total_questions) * 100
        return round(accuracy, 1)
    
    def get_game_iq(self) -> int:
        """Get current Game IQ score."""
        profile = self.get_profile() or {}
        return int(profile.get("game_iq", 100))
    
    def get_statistics(self) -> Dict[str, any]:
        """Get all statistics for Profile display."""
        profile = self.get_profile() or {}
        return {
            "total_questions_answered": profile.get("total_questions_answered", 0),
            "total_correct_answers": profile.get("total_correct_answers", 0),
            "total_games_played": profile.get("total_games_played", 0),
            "game_iq": self.get_game_iq(),
            "answer_accuracy": self.get_answer_accuracy(),
            "max_score": profile.get("max_score", 0),
            "total_win": profile.get("total_win", 0)
        }