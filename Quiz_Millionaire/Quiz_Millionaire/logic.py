import json
import random
from typing import List, Dict, Any, Optional
import os


class QuizEngine:
    def __init__(self, filename: str = "questions.json") -> None:
        """
        Инициализирует движок викторины.

        При старте загружает все вопросы из JSON и формирует
        набор из 15 случайных вопросов по уровням сложности 1–15.
        """
        self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        self.filename = os.path.join(self.BASE_DIR, filename)

        # Все вопросы из базы, разбитые по уровням сложности
        # {уровень: [список_вопросов]}
        self.all_questions: Dict[int, List[Dict[str, Any]]] = {}

        # Текущая игровая сессия: ровно по одному вопросу на каждый уровень 0–14 (уровни 1–15)
        self.current_game_questions: List[Optional[Dict[str, Any]]] = []

        # Текущий уровень (0..14). 0 — первый вопрос, 14 — последний.
        self.current_level: int = 0
        self.current_question_data: Optional[Dict[str, Any]] = None

        # Состояние подсказок
        self.used_hints: Dict[str, bool] = {
            "50_50": False,
            "audience": False,
        }

        # Track used questions to prevent repetition in the same session/back-to-back games
        self.used_question_ids: List[int] = []

        # Language-aware questions
        self.language: str = self._load_language_from_config()
        print(f"DEBUG: Current Language setting: [{self.language}]")
        try:
            from database import DatabaseManager
            self.db_manager = DatabaseManager()
        except Exception:
            self.db_manager = None

        self._load_data()
        self._init_current_game_questions()

    def _load_language_from_config(self) -> str:
        try:
            cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if not os.path.exists(cfg_path):
                return "ru"
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            lang = (cfg.get("language") or "ru").strip().lower()
            if lang in {"ru", "ky", "en"}:
                return lang
            return "ru"
        except Exception:
            return "ru"

    def set_language(self, language: str) -> None:
        """Switch question language and immediately rebuild current game questions."""
        language = (language or "").strip().lower()
        if language not in {"ru", "ky", "en"}:
            language = "ru"
        if language == self.language:
            return
        self.language = language
        self.prepare_new_game()

    def _load_data(self) -> None:
        """Загружает и валидирует данные из JSON файла (формат как в questions.json)."""
        try:
            if not os.path.exists(self.filename):
                print(f"WARNING: Question file '{self.filename}' not found. Falling back to database.")
                return
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"WARNING: Failed to load '{self.filename}': {e}. Falling back to database.")
            return

        if not isinstance(data, dict):
            raise ValueError("JSON файл должен содержать объект с уровнями сложности в качестве ключей.")

        all_questions: Dict[int, List[Dict[str, Any]]] = {}

        for level_key, questions in data.items():
            try:
                level = int(level_key)
            except (TypeError, ValueError):
                continue

            if not isinstance(questions, list):
                continue

            valid_questions: List[Dict[str, Any]] = []
            for q in questions:
                if (
                    isinstance(q, dict)
                    and "question" in q
                    and "options" in q
                    and "correct_index" in q
                ):
                    valid_questions.append(q)

            if valid_questions:
                all_questions[level] = valid_questions

        if not all_questions:
            print("WARNING: No valid questions loaded from JSON file.")

        self.all_questions = all_questions

    def _init_current_game_questions(self) -> None:
        """
        Формирует список из 15 вопросов для текущей игры.

        Для каждого уровня сложности от 1 до 15 выбирается один случайный вопрос
        из всех доступных вопросов этого уровня.
        """
        self.current_game_questions = []

        # If we are not using Russian language, build a fallback pool so we still
        # keep the language consistent for all 15 questions even if the DB has
        # only a few sample questions for that language.
        fallback_pool: List[Dict[str, Any]] = []
        if self.db_manager is not None and self.language != "ru":
            try:
                pool = self.db_manager.get_random_questions(list(range(1, 16)), self.language, 1)
                fallback_pool = [q for q in pool if q is not None]  # type: ignore[list-item]
            except Exception:
                fallback_pool = []

        for level in range(1, 16):
            chosen: Optional[Dict[str, Any]] = None

            # Prefer DB language-filtered questions when available.
            if self.db_manager is not None:
                try:
                    # Pass the used_question_ids to the database to exclude them
                    q_list = self.db_manager.get_random_questions(
                        [level], 
                        self.language, 
                        1, 
                        exclude_ids=self.used_question_ids
                    )
                    chosen = q_list[0] if q_list else None
                except Exception:
                    chosen = None

            # If DB has nothing for this language/level, keep language consistent using fallback_pool.
            if chosen is None and fallback_pool:
                # Filter fallback pool to avoid already chosen IDs
                available_pool = [
                    p for p in fallback_pool 
                    if p and p.get("id") not in self.used_question_ids
                ]
                if not available_pool:
                    available_pool = [p for p in fallback_pool if p]
                
                if available_pool:
                    chosen = random.choice(available_pool)

            # Fallback to JSON questions (RU-only) if DB has nothing at all.
            if chosen is None:
                level_questions = self.all_questions.get(level, [])
                if level_questions:
                    chosen = random.choice(level_questions)

            if chosen:
                self.current_game_questions.append(chosen)
                # Track the ID if it exists (DB questions have it, JSON ones might not)
                q_id = chosen.get("id")
                if q_id is not None:
                    self.used_question_ids.append(q_id)

        # Сбрасываем текущий уровень и активный вопрос
        self.current_level = 0
        self.current_question_data = None
        # Сбрасываем подсказки
        self.used_hints = {
            "50_50": False,
            "audience": False,
        }

    def prepare_new_game(self) -> None:
        """
        Подготавливает новую игру: формирует новый набор вопросов и
        сбрасывает прогресс и подсказки.
        """
        # Clear used questions at the start of a new game session to satisfy requirement 2.
        # Note: If we want to prevent repeats IN back-to-back games, we should NOT clear this
        # entirely, but the user specifically asked to clear it at the start of every new session.
        self.used_question_ids = []
        self._init_current_game_questions()

    def get_current_question(self) -> Optional[Dict[str, Any]]:
        """
        Возвращает вопрос для текущего уровня из списка current_game_questions.

        Если вопросы закончились или для уровня нет вопроса, возвращает None.
        """
        if 0 <= self.current_level < len(self.current_game_questions):
            return self.current_game_questions[self.current_level]
        return None

    def get_question(self) -> Optional[Dict[str, Any]]:
        """
        Совместимый метод для UI: возвращает текущий вопрос,
        используя предвыбранный список current_game_questions.
        """
        self.current_question_data = self.get_current_question()
        return self.current_question_data

    def check_answer(self, index: int) -> bool:
        """Проверяет ответ пользователя и продвигает уровень при успехе."""
        if self.current_question_data is None:
            raise RuntimeError("Вопрос еще не получен.")

        correct_index = self.current_question_data.get("correct_index")

        if index == correct_index:
            self.current_level += 1
            self.current_question_data = None
            return True

        return False

    def hint_50_50(self) -> List[int]:
        """Подсказка '50 на 50'. Возвращает индексы неверных ответов для скрытия."""
        if self.current_question_data is None:
            raise RuntimeError("Нет активного вопроса.")
        
        if self.used_hints['50_50']:
            raise RuntimeError("Подсказка 50/50 уже использована.")
        
        self.used_hints['50_50'] = True
        
        correct_index = self.current_question_data["correct_index"]
        answers = self.current_question_data.get("options", [])
        answers_count = len(answers)
        
        all_indices = list(range(answers_count))
        wrong_indices = [i for i in all_indices if i != correct_index]
        
        # Выбираем 2 неверных ответа
        count_to_remove = min(2, len(wrong_indices))
        removed_indices = random.sample(wrong_indices, count_to_remove)
        
        return sorted(removed_indices)

    def hint_audience(self) -> Dict[int, float]:
        """Подсказка 'Помощь зала'. Генерирует вероятности."""
        if self.current_question_data is None:
            raise RuntimeError("Нет активного вопроса.")
        
        if self.used_hints['audience']:
            raise RuntimeError("Подсказка 'Помощь зала' уже использована.")
        
        self.used_hints['audience'] = True
        
        correct_index = self.current_question_data["correct_index"]
        answers = self.current_question_data.get("options", [])
        answers_count = len(answers)
        
        probabilities = {}
        correct_prob = random.randint(60, 80)
        remaining_prob = 100 - correct_prob
        
        wrong_indices = [i for i in range(answers_count) if i != correct_index]
        
        if not wrong_indices:
            probabilities[correct_index] = 100.0
            return probabilities
            
        weights = [random.randint(1, 10) for _ in wrong_indices]
        total_weight = sum(weights)
        
        current_sum = 0
        for i, idx in enumerate(wrong_indices):
            if i == len(wrong_indices) - 1:
                prob = remaining_prob - current_sum
            else:
                prob = int((weights[i] / total_weight) * remaining_prob)
                current_sum += prob
            probabilities[idx] = float(prob)
        
        probabilities[correct_index] = float(correct_prob)
        
        # Нормализация
        total = sum(probabilities.values())
        if total != 100.0:
            probabilities[correct_index] += (100.0 - total)
            
        return probabilities