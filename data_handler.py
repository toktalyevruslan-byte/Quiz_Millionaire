import json
import os
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, stats_file: str = "records.json", profile_file: str = "profile.json", settings_file: str = "settings.json"):
        self.stats_file = stats_file
        self.profile_file = profile_file
        self.settings_file = settings_file

    # ---------- Методы для званий ----------

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

    def get_player_records(self, player_name: str) -> List[Dict[str, any]]:
        scores = self._load_scores()
        return [score for score in scores if score.get("name") == player_name]

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

        # Нормализация структуры (на случай старого формата)
        profile.setdefault("name", "")
        profile.setdefault("total_games", 0)
        profile.setdefault("total_win", 0)
        profile.setdefault("max_score", 0)
        profile.setdefault("total_questions_answered", 0)
        profile.setdefault("total_correct_answers", 0)
        profile.setdefault("total_incorrect_answers", 0)
        profile.setdefault("iq_score", 0)

        profile["total_games"] = int(profile["total_games"]) + 1
        profile["total_win"] = int(profile["total_win"]) + int(money)
        profile["max_score"] = max(int(profile["max_score"]), int(money))

        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

    def update_correct_answers(self, correct: bool, level: int) -> None:
        profile = self.get_profile() or {}
        profile.setdefault("total_questions_answered", 0)
        profile.setdefault("total_correct_answers", 0)
        profile.setdefault("total_incorrect_answers", 0)
        profile.setdefault("iq_score", 0)

        profile["total_questions_answered"] += 1
        if correct:
            profile["total_correct_answers"] += 1
            # Баллы за верный ответ
            if level <= 5:
                profile["iq_score"] += 1
            elif level <= 10:
                profile["iq_score"] += 3
            else:
                profile["iq_score"] += 7
        else:
            profile["total_incorrect_answers"] += 1
            # Штраф за неверный ответ (меньше на сложных)
            if level <= 5:
                profile["iq_score"] -= 2
            elif level <= 10:
                profile["iq_score"] -= 1
            else:
                profile["iq_score"] -= 0.5

        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

    def create_profile(self, name: str) -> None:
        profile = {
            "name": name,
            "total_games": 0,
            "total_win": 0,
            "max_score": 0,
            "total_questions_answered": 0,
            "total_correct_answers": 0,
            "total_incorrect_answers": 0,
            "iq_score": 0
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

    # ---------- Методы для Достижений ----------

    ACHIEVEMENTS = {
        "first_game": {
            "id": "first_game",
            "name": "Первый шаг",
            "description": "Сыграть первую игру",
            "icon": "🎮",
            "condition": lambda profile: profile.get("total_games", 0) >= 1
        },
        "ten_games": {
            "id": "ten_games",
            "name": "Опытный игрок",
            "description": "Сыграть 10 игр",
            "icon": "🏆",
            "condition": lambda profile: profile.get("total_games", 0) >= 10
        },
        "fifty_games": {
            "id": "fifty_games",
            "name": "Ветеран",
            "description": "Сыграть 50 игр",
            "icon": "👑",
            "condition": lambda profile: profile.get("total_games", 0) >= 50
        },
        "earn_100k": {
            "id": "earn_100k",
            "name": "Сотня",
            "description": "Выиграть 100 000 ₽",
            "icon": "💰",
            "condition": lambda profile: profile.get("max_score", 0) >= 100000
        },
        "earn_500k": {
            "id": "earn_500k",
            "name": "Миллион",
            "description": "Выиграть 500 000 ₽",
            "icon": "💎",
            "condition": lambda profile: profile.get("max_score", 0) >= 500000
        },
        "earn_1m": {
            "id": "earn_1m",
            "name": "Миллионер",
            "description": "Выиграть 1 000 000 ₽",
            "icon": "👨‍💼",
            "condition": lambda profile: profile.get("max_score", 0) >= 1000000
        },
        "high_accuracy": {
            "id": "high_accuracy",
            "name": "Меткий стрелок",
            "description": "Достичь 80% точности ответов",
            "icon": "🎯",
            "condition": lambda profile: profile.get("_accuracy_80", False)
        },
        "perfect_game": {
            "id": "perfect_game",
            "name": "Идеальная игра",
            "description": "Правильно ответить на 10+ вопросов подряд",
            "icon": "⭐",
            "condition": lambda profile: profile.get("streak_correct", 0) >= 10
        },
        "iq_genius": {
            "id": "iq_genius",
            "name": "Гений",
            "description": "Достичь IQ 150+",
            "icon": "🧠",
            "condition": lambda profile: (70 + profile.get("iq_score", 0)) >= 150
        },
        "true_expert": {
            "id": "true_expert",
            "name": "Настоящий эксперт",
            "description": "Ответить правильно на 500+ вопросов",
            "icon": "🔥",
            "condition": lambda profile: profile.get("total_correct_answers", 0) >= 500
        },
    }

    def _check_accuracy(self, profile: Dict[str, any], threshold: float) -> bool:
        """Проверить точность ответов."""
        total = profile.get("total_questions_answered", 0)
        if total == 0:
            return False
        correct = profile.get("total_correct_answers", 0)
        accuracy = correct / total
        return accuracy >= threshold

    def get_achievements(self) -> Dict[str, any]:
        """Получить данные о достижениях."""
        achievements_file = "achievements.json"
        if os.path.exists(achievements_file):
            try:
                with open(achievements_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}

    def unlock_achievement(self, achievement_id: str) -> bool:
        """Разблокировать достижение."""
        achievements = self.get_achievements()
        if achievement_id not in achievements:
            achievements[achievement_id] = {
                "id": achievement_id,
                "unlocked": True,
                "unlocked_date": str(__import__('datetime').datetime.now())
            }
            self._save_achievements(achievements)
            return True
        return False

    def update_achievements(self) -> List[str]:
        """Обновить достижения на основе профиля. Возвращает список новых разблокированных."""
        profile = self.get_profile() or {}
        achievements = self.get_achievements()
        new_unlocked = []

        # Вычислить точность для проверки
        total = profile.get("total_questions_answered", 0)
        if total > 0:
            correct = profile.get("total_correct_answers", 0)
            accuracy = correct / total
            profile["_accuracy_80"] = accuracy >= 0.8
        else:
            profile["_accuracy_80"] = False

        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            # Если достижение уже разблокировано, пропустить
            if achievement_id in achievements:
                continue

            # Проверить условие разблокировки
            try:
                if achievement_data["condition"](profile):
                    self.unlock_achievement(achievement_id)
                    new_unlocked.append(achievement_id)
            except:
                pass

        return new_unlocked

    def get_unlocked_achievements(self) -> List[Dict[str, any]]:
        """Получить список разблокированных достижений."""
        achievements = self.get_achievements()
        unlocked = []

        for achievement_id in achievements.keys():
            if achievement_id in self.ACHIEVEMENTS:
                achievement_data = self.ACHIEVEMENTS[achievement_id].copy()
                achievement_data["unlocked_date"] = achievements[achievement_id].get("unlocked_date")
                unlocked.append(achievement_data)

        return sorted(unlocked, key=lambda x: x["name"])

    def get_locked_achievements(self) -> List[Dict[str, any]]:
        """Получить список заблокированных достижений."""
        achievements = self.get_achievements()
        locked = []

        for achievement_id, achievement_data in self.ACHIEVEMENTS.items():
            if achievement_id not in achievements:
                data = achievement_data.copy()
                locked.append(data)

        return sorted(locked, key=lambda x: x["name"])

    def _save_achievements(self, achievements: Dict[str, any]) -> None:
        """Сохранить данные о достижениях."""
        achievements_file = "achievements.json"
        with open(achievements_file, 'w', encoding='utf-8') as f:
            json.dump(achievements, f, ensure_ascii=False, indent=4)
