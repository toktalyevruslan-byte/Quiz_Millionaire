import os

try:
    import pygame
except ImportError:
    pygame = None


class SoundManager:
    def __init__(self, sounds_dir: str = "assets/sounds"):
        self.sounds_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), sounds_dir))
        self.master_volume = 1.0
        self.music_volume = 0.5
        self.effects_volume = 0.5
        self.enabled = False
        self.effects_cache = {}

        if pygame is None:
            print("[SoundManager] pygame не установлен — звук отключен")
            return

        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            self.enabled = True
            print(f"[SoundManager] Инициализирован (путь: {self.sounds_dir}, volume={self.music_volume})")
        except Exception as exc:
            print(f"[SoundManager] Не удалось инициализировать pygame.mixer: {exc}")
            self.enabled = False

    def _resolve_path(self, filename: str) -> str:
        return os.path.abspath(os.path.join(self.sounds_dir, filename))

    def set_master_volume(self, volume: float) -> None:
        self.master_volume = max(0.0, min(1.0, volume))
        # Update both music and effects with the new master volume
        self.set_music_volume(self.music_volume)
        self.set_effects_volume(self.effects_volume)
        print(f"[SoundManager] Установлена общая громкость: {self.master_volume}")

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            try:
                pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            except Exception as exc:
                print(f"[SoundManager] Ошибка установки громкости музыки: {exc}")
        print(f"[SoundManager] Установлена громкость музыки: {self.music_volume} (итоговая: {self.music_volume * self.master_volume})")

    def set_effects_volume(self, volume: float) -> None:
        self.effects_volume = max(0.0, min(1.0, volume))
        actual_vol = self.effects_volume * self.master_volume
        print(f"[SoundManager] Установлена громкость эффектов: {self.effects_volume} (итоговая: {actual_vol})")
        for sound in self.effects_cache.values():
            try:
                sound.set_volume(actual_vol)
            except Exception:
                pass

    def set_volume(self, volume: float) -> None:
        self.set_master_volume(volume)

    def play_bg_music(self, filename: str) -> None:
        print(f"[SoundManager] Попытка запуска файла: {filename}")
        if not self.enabled:
            print("[SoundManager] Звук отключен: pygame mixer не инициализирован")
            return

        path = self._resolve_path(filename)
        print(f"[SoundManager] bg music path: {path}")
        if not os.path.exists(path):
            print(f"[SoundManager] Файл не найден: {path}")
            return

        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self.music_volume)
            pygame.mixer.music.play(-1)
            print(f"[SoundManager] Воспроизведение bg music: {path}")
        except Exception as exc:
            print(f"[SoundManager] Ошибка воспроизведения фоновой музыки: {exc}")

    def stop_bg_music(self) -> None:
        if not self.enabled:
            return
        try:
            pygame.mixer.music.stop()
            print("[SoundManager] Остановка фоновой музыки")
        except Exception as exc:
            print(f"[SoundManager] Ошибка остановки фоновой музыки: {exc}")

    def play_effect(self, filename: str) -> None:
        print(f"[SoundManager] Playing effect: {filename}")
        if not self.enabled:
            print("[SoundManager] Звук отключен: pygame mixer не инициализирован")
            return

        path = self._resolve_path(filename)
        print(f"[SoundManager] effect path: {path}")
        if not os.path.exists(path):
            print(f"[SoundManager] Файл не найден: {path}")
            return

        try:
            if path not in self.effects_cache:
                self.effects_cache[path] = pygame.mixer.Sound(path)
            effect = self.effects_cache[path]
            effect.set_volume(self.effects_volume)
            effect.play()
            print(f"[SoundManager] Воспроизведение эффекта: {path}")
        except Exception as exc:
            print(f"[SoundManager] Ошибка воспроизведения эффекта: {exc}")

    def play(self, filename: str) -> None:
        self.play_effect(filename)
