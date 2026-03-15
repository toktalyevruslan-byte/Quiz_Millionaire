from logic import QuizEngine
from ui import QuizApp
from sound_manager import SoundManager


def main() -> None:
    try:
        engine = QuizEngine()
    except Exception as exc:
        # Если возникла проблема с загрузкой questions.json,
        # выводим сообщение и не запускаем приложение, вместо
        # того чтобы сразу переходить к экрану завершения.
        print(f"Не удалось инициализировать игру: {exc}")
        return

    # Инициализируем звуковую подсистему до создания окна
    sound_manager = SoundManager()

    app = QuizApp(engine, sound_manager=sound_manager)
    app.mainloop()


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()