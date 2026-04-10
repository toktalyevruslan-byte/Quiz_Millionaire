import os
import threading

try:
    import pygame
    pygame.mixer.init()
except ImportError:
    pygame = None


class SoundManager:
    def __init__(self, sounds_dir: str = "assets/sounds"):
        # Абсолютный путь (от корня проекта)
        self.sounds_dir = os.path.abspath(sounds_dir)
        self.enabled = pygame is not None
        self.music_volume = 1.0
        self.effects_volume = 1.0
        self.bg_music_playing = False

        if not self.enabled:
            print("[SoundManager] pygame не установлен — звук отключен")
        else:
            print(f"[SoundManager] Инициализирован (путь: {self.sounds_dir})")

    def _resolve_path(self, filename: str) -> str:
        return os.path.abspath(os.path.join(self.sounds_dir, filename))

    def set_music_volume(self, volume: float) -> None:
        self.music_volume = max(0.0, min(1.0, volume))
        if self.enabled:
            pygame.mixer.music.set_volume(self.music_volume)
        print(f"[SoundManager] Установлена громкость музыки: {self.music_volume}")

    def set_effects_volume(self, volume: float) -> None:
        self.effects_volume = max(0.0, min(1.0, volume))
        print(f"[SoundManager] Установлена громкость эффектов: {self.effects_volume}")

    def play_bg_music(self, filename: str) -> None:
        print(f"[SoundManager] Playing background music: {filename}")
        if not self.enabled:
            return

        path = self._resolve_path(filename)
        print(f"[SoundManager] bg music path: {path}")
        if not os.path.exists(path):
            print(f"[SoundManager] Файл не найден: {path}")
            return

        self.stop_bg_music()

        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.bg_music_playing = True

    def stop_bg_music(self) -> None:
        if not self.enabled:
            return
        if self.bg_music_playing:
            pygame.mixer.music.stop()
        self.bg_music_playing = False

    def play(self, filename: str) -> None:
        print(f"[SoundManager] Playing sound: {filename}")
        if not self.enabled:
            return

        path = self._resolve_path(filename)
        print(f"[SoundManager] sound path: {path}")
        if not os.path.exists(path):
            print(f"[SoundManager] Файл не найден: {path}")
            return

        def _play_sound():
            try:
                sound = pygame.mixer.Sound(path)
                sound.set_volume(self.effects_volume)
                sound.play()
            except Exception as e:
                print(f"[SoundManager] Ошибка воспроизведения: {e}")

        threading.Thread(target=_play_sound, daemon=True).start()
