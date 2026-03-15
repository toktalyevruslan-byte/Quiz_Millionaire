import os
import threading
import multiprocessing

try:
    from playsound import playsound
except ImportError:
    playsound = None


def _playsound_process(path: str) -> None:
    try:
        playsound(path)
    except Exception as e:
        print(f"[SoundManager] Ошибка воспроизведения: {e}")


class SoundManager:
    def __init__(self, sounds_dir: str = "assets/sounds"):
        # Абсолютный путь (от корня проекта)
        self.sounds_dir = os.path.abspath(sounds_dir)
        self.enabled = playsound is not None
        self.bg_music_process = None

        if not self.enabled:
            print("[SoundManager] playsound не установлен — звук отключен")
        else:
            print(f"[SoundManager] Инициализирован (путь: {self.sounds_dir})")

    def _resolve_path(self, filename: str) -> str:
        return os.path.abspath(os.path.join(self.sounds_dir, filename))

    def set_volume(self, volume: float) -> None:
        # playsound не поддерживает изменение громкости, сохраняем значение для совместимости.
        self.volume = max(0.0, min(1.0, volume))
        print(f"[SoundManager] Установлена громкость (симулированно): {self.volume}")

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

        self.bg_music_process = multiprocessing.Process(
            target=_playsound_process,
            args=(path,),
            daemon=True,
        )
        self.bg_music_process.start()

    def stop_bg_music(self) -> None:
        if not self.enabled:
            return
        if self.bg_music_process is not None and self.bg_music_process.is_alive():
            try:
                self.bg_music_process.terminate()
            except Exception as e:
                print(f"[SoundManager] Ошибка остановки bg music: {e}")
        self.bg_music_process = None

    def play(self, filename: str) -> None:
        print(f"[SoundManager] Playing sound: {filename}")
        if not self.enabled:
            return

        path = self._resolve_path(filename)
        print(f"[SoundManager] sound path: {path}")
        if not os.path.exists(path):
            print(f"[SoundManager] Файл не найден: {path}")
            return

        threading.Thread(target=_playsound_process, args=(path,), daemon=True).start()
