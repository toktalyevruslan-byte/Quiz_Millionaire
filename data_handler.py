import json
import os
from typing import List, Dict, Optional

class DataManager:
    def __init__(self, stats_file: str = "records.json", profile_file: str = "profile.json"):
        self.stats_file = stats_file
        self.profile_file = profile_file

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

        profile["total_games"] = int(profile["total_games"]) + 1
        profile["total_win"] = int(profile["total_win"]) + int(money)

        with open(self.profile_file, 'w', encoding='utf-8') as f:
            json.dump(profile, f, ensure_ascii=False, indent=4)

    # ---------- Методы для Настроек ----------

    def clear_all_data(self) -> None:
        if os.path.exists(self.stats_file):
            os.remove(self.stats_file)
        if os.path.exists(self.profile_file):
            os.remove(self.profile_file)