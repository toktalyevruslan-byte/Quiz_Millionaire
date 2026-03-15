import json
import random
from typing import List, Dict, Any, Optional


class QuizEngine:
    def __init__(self, filename: str = "questions.json") -> None:
        """
        Инициализирует движок викторины.

        При старте загружает все вопросы из JSON и формирует
        набор из 15 случайных вопросов по уровням сложности 1–15.
        """
        self.filename = filename

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

        self._load_data()
        self._init_current_game_questions()

    def _load_data(self) -> None:
        """Загружает и валидирует данные из JSON файла (формат как в questions.json)."""
        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Файл с вопросами '{self.filename}' не найден.")
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(f"Ошибка парсинга JSON: {e.msg}", e.doc, e.pos)

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
            raise ValueError("Не удалось загрузить ни одного корректного вопроса из JSON файла.")

        self.all_questions = all_questions

    def _init_current_game_questions(self) -> None:
        """
        Формирует список из 15 вопросов для текущей игры.

        Для каждого уровня сложности от 1 до 15 выбирается один случайный вопрос
        из всех доступных вопросов этого уровня.
        """
        self.current_game_questions = []

        for level in range(1, 16):
            level_questions = self.all_questions.get(level, [])
            if level_questions:
                chosen = random.choice(level_questions)
            else:
                chosen = None
            self.current_game_questions.append(chosen)

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