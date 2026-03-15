import customtkinter as ctk
from typing import Optional
from logic import QuizEngine
import os
from data_handler import DataManager
from sound_manager import SoundManager

# Тёмная тема
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def load_fonts():
    """Проверяет наличие .ttf файлов в папке /assets/fonts/ и регистрирует их.
    Если файлов нет, использует стандартные системные аналоги."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    
    # Шрифты для вопросов и ответов: Conduit ITC или аналог
    conduit_path = os.path.join(fonts_dir, "Conduit ITC Regular.otf")
    if os.path.exists(conduit_path):
        question_font_family = "Conduit ITC"
    else:
        question_font_family = "Arial Narrow"  # Аналог, если нет файла
    
    # Шрифты для денежной лестницы и логотипа: Copperplate Gothic Bold или serif аналог
    copperplate_path = os.path.join(fonts_dir, "copperplategothic_bold.ttf")
    if os.path.exists(copperplate_path):
        ladder_font_family = "Copperplate Gothic Bold"
    else:
        ladder_font_family = "Georgia"  # Serif аналог
    
    # Шрифт для номера вопроса: Montserrat Bold или Verdana Bold
    verdana_path = os.path.join(fonts_dir, "ofont.ru_Verdana.ttf")
    if os.path.exists(verdana_path):
        number_font_family = "Verdana"
    else:
        number_font_family = "Verdana"  # Системный
    
    return {
        "question": question_font_family,
        "ladder": ladder_font_family,
        "number": number_font_family,
    }

# Загрузка шрифтов
FONTS = load_fonts()


class QuizApp(ctk.CTk):
    def __init__(self, engine: QuizEngine, sound_manager: Optional[SoundManager] = None) -> None:
        super().__init__()

        self.engine = engine
        self.data_manager = DataManager()
        self.sound_manager = sound_manager or SoundManager()

        self.prize_levels = []
        self.title("Кто хочет стать миллионером?")
        self.geometry("1200x700")
        self.resizable(False, False)

        # Состояние
        self.is_processing: bool = False
        self.current_question_data: Optional[dict] = None
        self.time_left: int = 0
        self._timer_id: Optional[str] = None

        # Подсказки (UI-уровень)
        self.used_call_friend: bool = False
        self.safety_net_active: bool = False

        # Фреймы экранов
        self.menu_frame: Optional[ctk.CTkFrame] = None
        self.lifeline_frame: Optional[ctk.CTkFrame] = None
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.sidebar_frame: Optional[ctk.CTkFrame] = None

        # Сетка окна: 0 — подсказки, 1 — центр, 2 — лестница
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Показать главное меню
        self.show_main_menu()

    # ---------- Главное меню ----------

    def show_main_menu(self) -> None:
        # Остановить текущую музыку (если была) и запустить музыку меню
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music("main_theme.mp3")

        if self.lifeline_frame is not None:
            self.lifeline_frame.destroy()
            self.lifeline_frame = None
        if self.main_frame is not None:
            self.main_frame.destroy()
            self.main_frame = None
        if self.sidebar_frame is not None:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None

        if self.menu_frame is not None:
            self.menu_frame.destroy()

        # Основной фрейм главного экрана с тёмно-синим фоном
        self.menu_frame = ctk.CTkFrame(self, fg_color="#020b23")
        self.menu_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.menu_frame.grid_columnconfigure(0, weight=1)
        self.menu_frame.grid_rowconfigure(0, weight=1)   # верхняя часть (зал)
        self.menu_frame.grid_rowconfigure(1, weight=0)   # кнопка играть
        self.menu_frame.grid_rowconfigure(2, weight=0)   # нижняя панель

        # Верхняя зона с "зал студии" и заголовком
        top_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=(20, 10))
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_rowconfigure(1, weight=0)

        # Условный фон студии (можно потом заменить картинкой)
        studio_frame = ctk.CTkFrame(top_frame, fg_color="#041637", corner_radius=40)
        studio_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        studio_frame.grid_columnconfigure(0, weight=1)
        studio_frame.grid_rowconfigure(0, weight=1)

        # Заглушка для силуэта сцены/кресел
        center_label = ctk.CTkLabel(
            studio_frame,
            text="",
            fg_color="#030d24",
        )
        center_label.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

        # Золотой баннер с названием игры
        title_frame = ctk.CTkFrame(
            top_frame,
            fg_color="#071a3d",
            corner_radius=30,
        )
        title_frame.grid(row=1, column=0, pady=(0, 10))
        title_label = ctk.CTkLabel(
            title_frame,
            text="КТО ХОЧЕТ СТАТЬ МИЛЛИОНЕРОМ?",
            font=ctk.CTkFont(family=FONTS["ladder"], size=26, weight="bold"),
            text_color="#ffd700",
            padx=40,
            pady=12,
        )
        title_label.pack()

        # Большая кнопка "ИГРАТЬ" в стиле кристалла
        play_btn = ctk.CTkButton(
            self.menu_frame,
            text="ИГРАТЬ",
            font=ctk.CTkFont(size=26, weight="bold"),
            width=320,
            height=80,
            fg_color="#0d5ecd",
            hover_color="#1a75ff",
            text_color="#ffd700",
            corner_radius=40,
            border_width=3,
            border_color="#4fd5ff",
            command=self.start_game,
        )
        play_btn.grid(row=1, column=0, pady=(0, 10), sticky="n")

        # Нижняя панель с иконками и подписями
        bottom_frame = ctk.CTkFrame(self.menu_frame, fg_color="transparent")
        bottom_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(10, 20))
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)

        left_panel = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        left_panel.grid(row=0, column=0, sticky="w")

        right_panel = ctk.CTkFrame(bottom_frame, fg_color="transparent")
        right_panel.grid(row=0, column=1, sticky="e")

        # Кнопки слева: Настройки и Рекорды
        settings_btn = ctk.CTkButton(
            left_panel,
            text="⚙  НАСТРОЙКИ",
            fg_color="#10233f",
            hover_color="#193762",
            corner_radius=25,
            width=150,
            command=self.show_settings_window,
        )
        settings_btn.grid(row=0, column=0, padx=5, pady=5)

        records_btn = ctk.CTkButton(
            left_panel,
            text="🏅  РЕКОРДЫ",
            fg_color="#10233f",
            hover_color="#193762",
            corner_radius=25,
            width=150,
            command=self.show_records,
        )
        records_btn.grid(row=0, column=1, padx=5, pady=5)

        # Кнопки справа: Профиль и Выход
        profile_btn = ctk.CTkButton(
            right_panel,
            text="👤  ПРОФИЛЬ",
            fg_color="#10233f",
            hover_color="#193762",
            corner_radius=25,
            width=150,
            command=self.show_profile_window,
        )
        profile_btn.grid(row=0, column=0, padx=5, pady=5)

        exit_btn = ctk.CTkButton(
            right_panel,
            text="⏻  ВЫХОД",
            fg_color="#7a1212",
            hover_color="#a31919",
            corner_radius=25,
            width=150,
            command=self.destroy,
        )
        exit_btn.grid(row=0, column=1, padx=5, pady=5)

    def start_game(self) -> None:
        if self.menu_frame is not None:
            self.menu_frame.destroy()
            self.menu_frame = None

        # Переход в игру — смена фоновой музыки
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music("question_background.mp3")

        self.engine.prepare_new_game()
        self.is_processing = False
        self.current_question_data = None
        self.used_call_friend = False
        self.safety_net_active = False

        self._create_lifeline_panel()
        self._create_main_area()
        self._create_sidebar()

        self.load_next_question()

    # ---------- Игровые панели ----------

    def _create_lifeline_panel(self) -> None:
        self.lifeline_frame = ctk.CTkFrame(self, fg_color="#041021")
        self.lifeline_frame.grid(row=0, column=0, sticky="nsew")
        self.lifeline_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.lifeline_frame.grid_columnconfigure(0, weight=1)

        cfg = {
            "width": 150,
            "height": 70,
            "corner_radius": 35,
            "fg_color": "#10233f",
            "hover_color": "#1a3b66",
            "text_color": "#e6e6e6",
            "font": ctk.CTkFont(size=14, weight="bold"),
        }

        self.btn_5050 = ctk.CTkButton(
            self.lifeline_frame,
            text="50 : 50",
            command=self.use_hint_5050,
            **cfg,
        )
        self.btn_5050.grid(row=0, column=0, pady=15, padx=10, sticky="n")

        self.btn_call_friend = ctk.CTkButton(
            self.lifeline_frame,
            text="ЗВОНОК\nДРУГУ",
            command=self._on_call_friend,
            **cfg,
        )
        self.btn_call_friend.grid(row=1, column=0, pady=15, padx=10, sticky="n")

        self.btn_audience = ctk.CTkButton(
            self.lifeline_frame,
            text="ПОМОЩЬ\nЗАЛА",
            command=self.use_hint_audience,
            **cfg,
        )
        self.btn_audience.grid(row=2, column=0, pady=15, padx=10, sticky="n")

        self.btn_second_chance = ctk.CTkButton(
            self.lifeline_frame,
            text="ПРАВО\nНА ОШИБКУ",
            command=self._on_second_chance,
            **cfg,
        )
        self.btn_second_chance.grid(row=3, column=0, pady=15, padx=10, sticky="n")

    def _create_main_area(self) -> None:
        self.main_frame = ctk.CTkFrame(self, fg_color="#020b23")
        self.main_frame.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=2)
        self.main_frame.grid_rowconfigure(2, weight=3)
        self.main_frame.grid_rowconfigure(3, weight=0)
        self.main_frame.grid_columnconfigure((0, 1), weight=1)

        self.question_header_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(family=FONTS["number"], size=28, weight="bold"),
            text_color="#ffffff",
        )
        self.question_header_label.grid(row=0, column=0, columnspan=2, pady=(10, 10))

        self.question_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(family=FONTS["question"], size=22, weight="bold"),
            wraplength=650,
            justify="center",
            fg_color="#061839",
            text_color="#ffffff",
            corner_radius=30,
        )
        self.question_label.grid(row=1, column=0, columnspan=2, padx=40, pady=(0, 20), sticky="nsew")

        self.answer_buttons = []
        for i in range(4):
            row = 2 + i // 2
            col = i % 2
            self.main_frame.grid_rowconfigure(row, weight=1)
            btn = ctk.CTkButton(
                self.main_frame,
                text=f"{chr(ord('A') + i)}: ",
                font=ctk.CTkFont(family=FONTS["question"], size=18, weight="bold"),
                height=60,
                corner_radius=30,
                fg_color="#10233f",
                hover_color="#1a3b66",
                text_color="#ffd271",
                border_width=2,
                border_color="#ffd271",
                command=lambda idx=i: self.handle_click(idx),
            )
            btn.grid(row=row, column=col, padx=30, pady=8, sticky="nsew")
            self.answer_buttons.append(btn)

        self.timer_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
        )
        self.timer_label.grid(row=3, column=0, columnspan=2, pady=(10, 5))

    def _create_sidebar(self) -> None:
        self.sidebar_frame = ctk.CTkFrame(self, width=220, fg_color="#050e2a")
        self.sidebar_frame.grid(row=0, column=2, sticky="nsew", pady=20, padx=(0, 20))
        self.sidebar_frame.grid_propagate(False)

        title = ctk.CTkLabel(
            self.sidebar_frame,
            text="ДЕНЕЖНАЯ ЛЕСТНИЦА",
            font=ctk.CTkFont(family=FONTS["ladder"], size=18, weight="bold"),
            text_color="#ffd700",
        )
        title.pack(pady=(20, 10))

        self.prize_levels = [
            "1 000", "2 000", "3 000", "5 000", "10 000",
            "20 000", "40 000", "80 000", "160 000", "320 000",
            "640 000", "1 250 000", "2 500 000", "5 000 000", "10 000 000"
        ]

        self.prize_labels = []
        for i, amount in enumerate(reversed(self.prize_levels)):
            lbl = ctk.CTkLabel(
                self.sidebar_frame,
                text=f"{15 - i:2d}: {amount} ₽",
                font=ctk.CTkFont(family=FONTS["ladder"], size=14),
                anchor="e",
                padx=10,
                text_color="#b0b5d8",
            )
            lbl.pack(fill="x", pady=2)
            self.prize_labels.append(lbl)

        self.update_money_ladder()

    # ---------- Обновление UI и таймера ----------

    def update_ui(self) -> None:
        if not self.current_question_data:
            return

        self.question_header_label.configure(
            text=f"ВОПРОС №{self.engine.current_level + 1}"
        )
        self.question_label.configure(text=self.current_question_data["question"])

        options = self.current_question_data.get("options", [])
        for i, btn in enumerate(self.answer_buttons):
            if i < len(options):
                btn.configure(
                    text=f"{chr(ord('A') + i)}: {options[i]}",
                    fg_color="#10233f",
                    hover_color="#1a3b66",
                    text_color="#ffd271",
                    border_color="#ffd271",
                    state="normal",
                )
            else:
                btn.configure(text="", state="disabled")

        # Обновление состояний подсказок
        self.btn_5050.configure(
            state="disabled" if self.engine.used_hints.get("50_50") else "normal",
            fg_color="#555555" if self.engine.used_hints.get("50_50") else "#10233f",
        )
        self.btn_audience.configure(
            state="disabled" if self.engine.used_hints.get("audience") else "normal",
            fg_color="#555555" if self.engine.used_hints.get("audience") else "#10233f",
        )
        self.btn_call_friend.configure(
            state="disabled" if self.used_call_friend else "normal",
            fg_color="#555555" if self.used_call_friend else "#10233f",
        )
        if self.safety_net_active:
            self.btn_second_chance.configure(
                fg_color="#15803d", hover_color="#16a34a", text_color="#ffffff"
            )
        else:
            self.btn_second_chance.configure(
                fg_color="#10233f", hover_color="#1a3b66", text_color="#e6e6e6"
            )

        # Таймер
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        self.time_left = 30
        self._update_timer_label()
        self._start_timer()

    def _update_timer_label(self) -> None:
        self.timer_label.configure(text=f"ОСТАЛОСЬ ВРЕМЕНИ: {self.time_left} c.")

    def _start_timer(self) -> None:
        def tick() -> None:
            self.time_left -= 1
            if self.time_left <= 0:
                self.time_left = 0
                self._update_timer_label()
                self._timer_id = None
                self.show_game_over(win=False)
                return
            self._update_timer_label()
            self._timer_id = self.after(1000, tick)

        self._timer_id = self.after(1000, tick)

    def update_money_ladder(self) -> None:
        level = self.engine.current_level
        max_levels = len(self.prize_levels)
        for i, lbl in enumerate(self.prize_labels):
            real_level_idx = max_levels - 1 - i
            if real_level_idx == level:
                lbl.configure(text_color="#ffd700", font=ctk.CTkFont(family=FONTS["ladder"], size=16, weight="bold"))
                lbl.configure(fg_color="#444444", corner_radius=5)
            elif real_level_idx < level:
                lbl.configure(text_color="#00ff00", font=ctk.CTkFont(family=FONTS["ladder"], size=14))
                lbl.configure(fg_color="transparent")
            else:
                lbl.configure(text_color="#b0b5d8", font=ctk.CTkFont(family=FONTS["ladder"], size=14))
                lbl.configure(fg_color="transparent")

    # ---------- Логика вопросов ----------

    def load_next_question(self) -> None:
        try:
            self.current_question_data = self.engine.get_question()
            if not self.current_question_data:
                # Если вопросов не осталось — победа
                self.show_game_over(win=True)
                return
            self.update_ui()
            self.update_money_ladder()
            self.is_processing = False
        except Exception as e:
            print(f"Ошибка загрузки вопроса: {e}")

    def handle_click(self, index: int) -> None:
        if self.is_processing or not self.current_question_data:
            return

        # Остановим таймер
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        self.is_processing = True
        btn = self.answer_buttons[index]
        btn.configure(fg_color="#ffff00", text_color="black")
        self.after(1000, lambda: self.finalize_answer(index, btn))

    def finalize_answer(self, index: int, btn: ctk.CTkButton) -> None:
        correct_index = self.current_question_data.get("correct_index", -1)
        is_correct = index == correct_index

        if is_correct:
            self.sound_manager.play("correct_answer.mp3")
            self.engine.check_answer(index)
            btn.configure(fg_color="#2e7d32", text_color="white")

            def after_correct() -> None:
                next_question = self.engine.get_current_question()
                if next_question is None:
                    self.show_game_over(win=True)
                else:
                    self.load_next_question()

            self.after(1500, after_correct)
            return

        # Неверный ответ
        if self.safety_net_active:
            self.safety_net_active = False
            btn.configure(fg_color="#b71c1c", text_color="white")

            def restore() -> None:
                for b in self.answer_buttons:
                    if not b.cget("text"):
                        b.configure(state="disabled")
                        continue
                    b.configure(
                        fg_color="#10233f",
                        hover_color="#1a3b66",
                        text_color="#ffd271",
                        border_color="#ffd271",
                        state="normal",
                    )
                self.time_left = 30
                self._update_timer_label()
                self._start_timer()

                dialog = ctk.CTkToplevel(self)
                dialog.title("Право на ошибку")
                dialog.geometry("360x160")
                label = ctk.CTkLabel(
                    dialog,
                    text="У вас было право на ошибку! Попробуйте еще раз.",
                    wraplength=320,
                )
                label.pack(padx=20, pady=20)
                ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 15))

            self.after(800, restore)
            self.is_processing = False
            return

        # Неверный ответ: остановить фоновую музыку и проиграть звуковой эффект
        self.sound_manager.stop_bg_music()
        self.sound_manager.play("wrong_answer.mp3")
        btn.configure(fg_color="#b71c1c", text_color="white")
        self.after(1500, lambda: self.show_game_over(win=False))

    # ---------- Подсказки ----------

    def use_hint_5050(self) -> None:
        if self.is_processing or self.engine.used_hints.get("50_50", False):
            return
        try:
            indices = self.engine.hint_50_50()
            for idx in indices:
                self.answer_buttons[idx].configure(
                    fg_color="transparent",
                    text="",
                    state="disabled",
                    border_width=0,
                )
            self.sound_manager.play("lifeline_used.mp3")
            self.btn_5050.configure(state="disabled", fg_color="#555555")
        except Exception as e:
            print(f"Ошибка подсказки 50/50: {e}")

    def use_hint_audience(self) -> None:
        if self.is_processing or self.engine.used_hints.get("audience", False):
            return
        try:
            stats = self.engine.hint_audience()
            options = self.current_question_data.get("options", [])
            msg = "Голоса зала:\n"
            for idx, prob in sorted(stats.items(), key=lambda x: x[1], reverse=True):
                if 0 <= idx < len(options):
                    msg += f"{chr(ord('A') + idx)}: {options[idx]} — {prob:.1f}%\n"

            dialog = ctk.CTkToplevel(self)
            dialog.title("Помощь зала")
            dialog.geometry("320x260")
            dialog.attributes("-topmost", True)

            label = ctk.CTkLabel(dialog, text=msg, font=ctk.CTkFont(size=14), justify="left")
            label.pack(padx=20, pady=20, fill="both", expand=True)
            ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=10)

            self.sound_manager.play("lifeline_used.mp3")
            self.btn_audience.configure(state="disabled", fg_color="#555555")
        except Exception as e:
            print(f"Ошибка подсказки зала: {e}")

    def _on_call_friend(self) -> None:
        if self.is_processing or self.used_call_friend or not self.current_question_data:
            return
        options = self.current_question_data.get("options", [])
        correct_index = self.current_question_data.get("correct_index", -1)
        if not options or not (0 <= correct_index < len(options)):
            return

        import random as _rnd

        if _rnd.random() < 0.7:
            idx = correct_index
        else:
            wrong = [i for i in range(len(options)) if i != correct_index]
            idx = _rnd.choice(wrong) if wrong else correct_index

        letter = chr(ord("A") + idx)
        text = options[idx]

        dialog = ctk.CTkToplevel(self)
        dialog.title("Звонок другу")
        dialog.geometry("420x200")
        msg = f"Ваш друг Алексей думает, что правильный ответ — вариант {letter}: {text}."
        label = ctk.CTkLabel(dialog, text=msg, wraplength=380)
        label.pack(padx=20, pady=30)
        ctk.CTkButton(dialog, text="OK", command=dialog.destroy).pack(pady=(0, 20))

        self.sound_manager.play("lifeline_used.mp3")
        self.used_call_friend = True
        self.btn_call_friend.configure(state="disabled", fg_color="#555555")

    def _on_second_chance(self) -> None:
        if self.safety_net_active or self.is_processing:
            return
        self.safety_net_active = True
        self.btn_second_chance.configure(
            fg_color="#15803d", hover_color="#16a34a", text_color="#ffffff"
        )

    # ---------- Окно профиля ----------

    def show_profile_window(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Профиль игрока")
        dialog.geometry("400x350")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#020b23")

        profile = self.data_manager.get_profile()

        if profile:
            # Карточка профиля
            avatar_label = ctk.CTkLabel(
                dialog,
                text="👤",
                font=ctk.CTkFont(size=60),
                text_color="#ffd700",
            )
            avatar_label.pack(pady=(20, 10))

            name_label = ctk.CTkLabel(
                dialog,
                text=profile["name"],
                font=ctk.CTkFont(family=FONTS["ladder"], size=24, weight="bold"),
                text_color="#ffd700",
            )
            name_label.pack(pady=(0, 20))

            stats_text = f"Всего игр: {profile['total_games']}\nОбщий выигрыш: {profile['total_win']} ₽"
            stats_label = ctk.CTkLabel(
                dialog,
                text=stats_text,
                font=ctk.CTkFont(size=16),
                text_color="#ffffff",
                justify="center",
            )
            stats_label.pack(pady=(0, 20))
        else:
            # Создание профиля
            prompt_label = ctk.CTkLabel(
                dialog,
                text="Введите ваше имя:",
                font=ctk.CTkFont(size=18),
                text_color="#ffffff",
            )
            prompt_label.pack(pady=(30, 10))

            name_entry = ctk.CTkEntry(
                dialog,
                placeholder_text="Имя игрока",
                width=250,
                font=ctk.CTkFont(size=16),
            )
            name_entry.pack(pady=(0, 20))

            def create_profile():
                name = name_entry.get().strip()
                if name:
                    self.profile_manager.create_profile(name)
                    dialog.destroy()
                    self.show_profile_window()  # Переоткрыть с профилем

            create_btn = ctk.CTkButton(
                dialog,
                text="Создать профиль",
                command=create_profile,
                fg_color="#0d5ecd",
                hover_color="#1a75ff",
            )
            create_btn.pack(pady=(0, 20))

        # Кнопка закрыть
        close_btn = ctk.CTkButton(
            dialog,
            text="Закрыть",
            command=dialog.destroy,
            fg_color="#7a1212",
            hover_color="#a31919",
        )
        close_btn.pack(pady=(10, 20))

    # ---------- Окно настроек ----------

    def show_settings_window(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Настройки")
        dialog.geometry("350x250")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#020b23")

        title_label = ctk.CTkLabel(
            dialog,
            text="НАСТРОЙКИ",
            font=ctk.CTkFont(family=FONTS["ladder"], size=20, weight="bold"),
            text_color="#ffd700",
        )
        title_label.pack(pady=(20, 30))

        volume_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        volume_frame.pack(fill="x", padx=20, pady=(0, 20))

        volume_label = ctk.CTkLabel(
            volume_frame,
            text="Громкость",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        volume_label.pack(anchor="w")

        volume_slider = ctk.CTkSlider(
            volume_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            command=lambda v: self.sound_manager.set_volume(v),
        )
        volume_slider.set(self.sound_manager.volume)
        volume_slider.pack(fill="x", pady=(10, 0))

        clear_btn = ctk.CTkButton(
            dialog,
            text="Очистить все данные",
            font=ctk.CTkFont(size=16),
            fg_color="#7a1212",
            hover_color="#a31919",
            command=lambda: self._confirm_clear_data(dialog),
        )
        clear_btn.pack(pady=(0, 20))

        close_btn = ctk.CTkButton(
            dialog,
            text="Закрыть",
            font=ctk.CTkFont(size=16),
            command=dialog.destroy,
        )
        close_btn.pack(pady=(10, 20))

    def _confirm_clear_data(self, parent_dialog) -> None:
        confirm_dialog = ctk.CTkToplevel(parent_dialog)
        confirm_dialog.title("Подтверждение")
        confirm_dialog.geometry("300x150")
        confirm_dialog.attributes("-topmost", True)
        confirm_dialog.configure(fg_color="#020b23")

        label = ctk.CTkLabel(
            confirm_dialog,
            text="Удалить все данные?\nЭто действие необратимо.",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        label.pack(pady=20)

        def yes():
            self.data_manager.clear_all_data()
            confirm_dialog.destroy()
            parent_dialog.destroy()
            # Можно показать сообщение об успехе

        yes_btn = ctk.CTkButton(confirm_dialog, text="Да", command=yes, fg_color="#7a1212", hover_color="#a31919")
        yes_btn.pack(side="left", padx=20, pady=10)

        no_btn = ctk.CTkButton(confirm_dialog, text="Нет", command=confirm_dialog.destroy)
        no_btn.pack(side="right", padx=20, pady=10)

    # ---------- Конец игры ----------

    def show_game_over(self, win: bool) -> None:
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        if self.lifeline_frame is not None:
            self.lifeline_frame.destroy()
            self.lifeline_frame = None
        if self.main_frame is not None:
            self.main_frame.destroy()
            self.main_frame = None
        if self.sidebar_frame is not None:
            self.sidebar_frame.destroy()
            self.sidebar_frame = None

        end_frame = ctk.CTkFrame(self, fg_color="transparent")
        end_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
        end_frame.grid_columnconfigure(0, weight=1)
        end_frame.grid_rowconfigure(0, weight=1)
        end_frame.grid_rowconfigure(1, weight=0)
        end_frame.grid_rowconfigure(2, weight=0)
        # Завершение игры — остановка фоновой музыки
        self.sound_manager.stop_bg_music()
        if win:
            title_text = "ПОЗДРАВЛЯЕМ!\nВЫ МИЛЛИОНЕР!"
            color = "#00ff00"
            win_amount = int(self.prize_levels[self.engine.current_level].replace(" ", "").replace("₽", ""))
            # Добавить рекорд
            self._add_record()
        else:
            title_text = "ИГРА ОКОНЧЕНА"
            color = "#ff0000"
            win_amount = 0

        self.data_manager.update_profile(win_amount)

        title_lbl = ctk.CTkLabel(
            end_frame,
            text=title_text,
            font=ctk.CTkFont(size=40, weight="bold"),
            text_color=color,
        )
        title_lbl.grid(row=0, column=0, pady=20)

        restart_btn = ctk.CTkButton(
            end_frame,
            text="Играть снова",
            font=ctk.CTkFont(size=20),
            command=lambda: self.restart_game(end_frame),
        )
        restart_btn.grid(row=2, column=0, pady=20)

    def restart_game(self, end_frame: ctk.CTkFrame) -> None:
        end_frame.destroy()
        self.engine.prepare_new_game()
        self.is_processing = False
        self.current_question_data = None
        self.used_call_friend = False
        self.safety_net_active = False
        self.show_main_menu()

    def show_records(self) -> None:
        records_window = ctk.CTkToplevel(self)
        records_window.title("Рекорды")
        records_window.geometry("500x600")
        records_window.configure(fg_color="#001122")  # Темно-синий фон

        # Заголовок
        title_label = ctk.CTkLabel(
            records_window,
            text="ТОП-10 РЕКОРДОВ",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFD700"  # Золотистый
        )
        title_label.pack(pady=20)

        # Получить топ-10
        top_records = self.data_manager.get_top_scores()

        # Фрейм для списка
        list_frame = ctk.CTkScrollableFrame(records_window, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Заголовки
        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        place_header = ctk.CTkLabel(header_frame, text="Место", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=80, anchor="w")
        place_header.pack(side="left", padx=5)
        name_header = ctk.CTkLabel(header_frame, text="Имя", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=200, anchor="w")
        name_header.pack(side="left", padx=5)
        score_header = ctk.CTkLabel(header_frame, text="Сумма", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=150, anchor="w")
        score_header.pack(side="left", padx=5)

        # Записи
        for i, record in enumerate(top_records, start=1):
            record_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            record_frame.pack(fill="x", pady=2)
            place_label = ctk.CTkLabel(record_frame, text=str(i), font=ctk.CTkFont(size=14), text_color="#FFD700", width=80, anchor="w")
            place_label.pack(side="left", padx=5)
            name_label = ctk.CTkLabel(record_frame, text=record["name"], font=ctk.CTkFont(size=14), text_color="#FFD700", width=200, anchor="w")
            name_label.pack(side="left", padx=5)
            score_label = ctk.CTkLabel(record_frame, text=f"{record['score']:,}", font=ctk.CTkFont(size=14), text_color="#FFD700", width=150, anchor="w")
            score_label.pack(side="left", padx=5)

        # Кнопка Закрыть
        close_btn = ctk.CTkButton(
            records_window,
            text="Закрыть",
            font=ctk.CTkFont(size=16),
            command=records_window.destroy
        )
        close_btn.pack(pady=20)

    def _add_record(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Новый рекорд!")
        dialog.geometry("300x200")
        dialog.attributes("-topmost", True)

        label = ctk.CTkLabel(dialog, text="Введите ваше имя:")
        label.pack(pady=20)

        name_entry = ctk.CTkEntry(dialog, placeholder_text="Имя")
        name_entry.pack(pady=10)

        def save_record():
            name = name_entry.get().strip()
            if name:
                score = self.prize_levels[self.engine.current_level]
                self.data_manager.save_score(name, score)
            dialog.destroy()

        save_btn = ctk.CTkButton(dialog, text="Сохранить", command=save_record)
        save_btn.pack(pady=10)
