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
