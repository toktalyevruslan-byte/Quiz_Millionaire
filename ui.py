import customtkinter as ctk
from typing import Optional
from logic import QuizEngine
import os
from data_handler import DataManager
from sound_manager import SoundManager
import json

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


class MainMenuFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="#020b23")
        self.app = app

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.grid(row=0, column=0, sticky="nsew", padx=40, pady=(20, 20))
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_rowconfigure(0, weight=1)
        top_frame.grid_rowconfigure(1, weight=0)

        studio_frame = ctk.CTkFrame(top_frame, fg_color="#041637", corner_radius=40)
        studio_frame.grid(row=0, column=0, sticky="nsew", pady=(0, 20))
        studio_frame.grid_columnconfigure(0, weight=1)
        studio_frame.grid_rowconfigure(0, weight=1)

        center_label = ctk.CTkLabel(
            studio_frame,
            text="",
            fg_color="#030d24",
        )
        center_label.grid(row=0, column=0, sticky="nsew", padx=40, pady=30)

        title_frame = ctk.CTkFrame(
            top_frame,
            fg_color="#071a3d",
            corner_radius=30,
        )
        title_frame.grid(row=1, column=0, pady=(0, 20))
        title_label = ctk.CTkLabel(
            title_frame,
            text="КТО ХОЧЕТ СТАТЬ МИЛЛИОНЕРОМ?",
            font=ctk.CTkFont(family=FONTS["ladder"], size=26, weight="bold"),
            text_color="#ffd700",
            padx=40,
            pady=12,
        )
        title_label.pack()

        play_btn = ctk.CTkButton(
            self,
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
            command=self.app.start_game,
        )
        play_btn.grid(row=1, column=0, pady=(0, 20), sticky="n")


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        # Заголовок
        title_label = ctk.CTkLabel(
            self,
            text="НАСТРОЙКИ",
            font=ctk.CTkFont(family=FONTS["question"], size=28, weight="bold"),
            text_color="#ffd700",
        )
        title_label.pack(pady=(30, 30))

        # Блок звука
        sound_frame = ctk.CTkFrame(self, fg_color="#041637", corner_radius=15)
        sound_frame.pack(fill="x", padx=40, pady=(0, 20))

        sound_title = ctk.CTkLabel(
            sound_frame,
            text="Звук",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        sound_title.pack(pady=(20, 10))

        # Громкость музыки
        music_frame = ctk.CTkFrame(sound_frame, fg_color="transparent")
        music_frame.pack(fill="x", padx=20, pady=(0, 10))

        music_label = ctk.CTkLabel(
            music_frame,
            text="Громкость музыки",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        music_label.pack(anchor="w")

        self.music_slider = ctk.CTkSlider(
            music_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            command=lambda v: self._set_music_volume(float(v)),
        )
        self.music_slider.pack(fill="x", pady=(5, 0))

        # Эффекты
        effects_frame = ctk.CTkFrame(sound_frame, fg_color="transparent")
        effects_frame.pack(fill="x", padx=20, pady=(10, 20))

        effects_label = ctk.CTkLabel(
            effects_frame,
            text="Эффекты",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        effects_label.pack(anchor="w")

        self.effects_slider = ctk.CTkSlider(
            effects_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            command=lambda v: self._set_effects_volume(float(v)),
        )
        self.effects_slider.pack(fill="x", pady=(5, 0))

        # Блок чекбоксов
        options_frame = ctk.CTkFrame(self, fg_color="#041637", corner_radius=15)
        options_frame.pack(fill="x", padx=40, pady=(0, 20))

        options_title = ctk.CTkLabel(
            options_frame,
            text="Опции",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#ffffff",
        )
        options_title.pack(pady=(20, 10))

        # Анимация текста
        self.animation_switch = ctk.CTkSwitch(
            options_frame,
            text="Анимация текста",
            font=ctk.CTkFont(size=14),
            command=self._toggle_animation,
        )
        self.animation_switch.pack(pady=(10, 10))

        # Таймер в игре
        self.timer_switch = ctk.CTkSwitch(
            options_frame,
            text="Таймер в игре",
            font=ctk.CTkFont(size=14),
            command=self._toggle_timer,
        )
        self.timer_switch.pack(pady=(10, 20))

        # Кнопка сброса рекордов
        reset_btn = ctk.CTkButton(
            self,
            text="Сбросить все рекорды",
            font=ctk.CTkFont(size=16),
            fg_color="#7a1212",
            hover_color="#a31919",
            command=self._confirm_reset_records,
        )
        reset_btn.pack(pady=(0, 20))

        # Загрузить настройки
        self._load_settings()

        back_btn = ctk.CTkButton(
            self,
            text="Назад",
            fg_color="#10233f",
            hover_color="#1a3b66",
            command=lambda: self.app.switch_frame(MainMenuFrame),
        )
        back_btn.pack(pady=(20, 20))

    def _load_settings(self) -> None:
        settings = self.app.data_manager.get_settings()
        music_vol = settings.get("music_volume", 0.5)
        effects_vol = settings.get("effects_volume", 0.5)
        animation = settings.get("animation_text", True)
        timer = settings.get("timer_in_game", True)

        self.music_slider.set(music_vol)
        self.effects_slider.set(effects_vol)
        self.animation_switch.select() if animation else self.animation_switch.deselect()
        self.timer_switch.select() if timer else self.timer_switch.deselect()

        self.app.sound_manager.set_music_volume(music_vol)
        self.app.sound_manager.set_effects_volume(effects_vol)

    def _set_music_volume(self, value: float) -> None:
        self.app.sound_manager.set_volume(value)
        self._save_settings()

    def _set_effects_volume(self, value: float) -> None:
        self.app.sound_manager.set_effects_volume(value)
        self._save_settings()

    def _toggle_animation(self) -> None:
        self._save_settings()

    def _toggle_timer(self) -> None:
        self._save_settings()

    def _save_settings(self) -> None:
        settings = {
            "music_volume": self.music_slider.get(),
            "effects_volume": self.effects_slider.get(),
            "animation_text": self.animation_switch.get(),
            "timer_in_game": self.timer_switch.get(),
        }
        self.app.data_manager.save_settings(settings)

    def _confirm_reset_records(self) -> None:
        dialog = ctk.CTkToplevel(self)
        dialog.title("Подтверждение")
        dialog.geometry("300x150")
        dialog.attributes("-topmost", True)
        dialog.configure(fg_color="#020b23")

        label = ctk.CTkLabel(
            dialog,
            text="Сбросить все рекорды?\nЭто действие необратимо.",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        label.pack(pady=20)

        def yes():
            self.app.data_manager.clear_all_data()
            dialog.destroy()

        yes_btn = ctk.CTkButton(dialog, text="Да", command=yes, fg_color="#7a1212", hover_color="#a31919")
        yes_btn.pack(side="left", padx=20, pady=10)

        no_btn = ctk.CTkButton(dialog, text="Нет", command=dialog.destroy)
        no_btn.pack(side="right", padx=20, pady=10)


class RecordsFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="#001122")
        self.app = app
        self.grid_columnconfigure(0, weight=1)

        title_label = ctk.CTkLabel(
            self,
            text="ТОП-10 РЕКОРДОВ",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FFD700",
        )
        title_label.pack(pady=20)

        top_records = self.app.data_manager.get_top_scores()

        list_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        header_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 10))
        place_header = ctk.CTkLabel(header_frame, text="Место", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=80, anchor="w")
        place_header.pack(side="left", padx=5)
        name_header = ctk.CTkLabel(header_frame, text="Имя", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=200, anchor="w")
        name_header.pack(side="left", padx=5)
        score_header = ctk.CTkLabel(header_frame, text="Сумма", font=ctk.CTkFont(size=16, weight="bold"), text_color="#FFD700", width=150, anchor="w")
        score_header.pack(side="left", padx=5)

        if not top_records:
            empty = ctk.CTkLabel(list_frame, text="Пока нет рекордов", font=ctk.CTkFont(size=16), text_color="#ffffff")
            empty.pack(pady=20)
        for i, record in enumerate(top_records, start=1):
            record_frame = ctk.CTkFrame(list_frame, fg_color="transparent")
            record_frame.pack(fill="x", pady=2)
            place_label = ctk.CTkLabel(record_frame, text=str(i), font=ctk.CTkFont(size=14), text_color="#FFD700", width=80, anchor="w")
            place_label.pack(side="left", padx=5)
            name_label = ctk.CTkLabel(record_frame, text=record["name"], font=ctk.CTkFont(size=14), text_color="#FFD700", width=200, anchor="w")
            name_label.pack(side="left", padx=5)
            score_label = ctk.CTkLabel(record_frame, text=f"{record['score']:,}", font=ctk.CTkFont(size=14), text_color="#FFD700", width=150, anchor="w")
            score_label.pack(side="left", padx=5)

        back_btn = ctk.CTkButton(
            self,
            text="Назад",
            fg_color="#10233f",
            hover_color="#1a3b66",
            command=lambda: self.app.switch_frame(MainMenuFrame),
        )
        back_btn.pack(pady=(20, 20))


class ProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="#020b23")
        self.app = app
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        profile = self.app.data_manager.get_profile()

        # ========== ВЕРХНЯЯ ПАНЕЛЬ ==========
        top_panel = ctk.CTkFrame(self, fg_color="transparent", height=60)
        top_panel.grid(row=0, column=0, sticky="ew", padx=20, pady=(15, 0))
        top_panel.grid_propagate(False)

        # Заголовок слева
        title_label = ctk.CTkLabel(
            top_panel,
            text="Millionaire Quiz Pro - Profile",
            font=ctk.CTkFont(family=FONTS.get("ladder", "Arial"), size=14),
            text_color="#ffffff",
        )
        title_label.pack(side="left", padx=10)

        # Время, колокольчик, шестеренка справа
        right_frame = ctk.CTkFrame(top_panel, fg_color="transparent")
        right_frame.pack(side="right")

        import time
        current_time = time.strftime("%H:%M")
        time_label = ctk.CTkLabel(
            right_frame,
            text=current_time,
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        time_label.pack(side="left", padx=5)

        bell_label = ctk.CTkLabel(
            right_frame,
            text="🔔",
            font=ctk.CTkFont(size=16),
        )
        bell_label.pack(side="left", padx=5)

        settings_label = ctk.CTkLabel(
            right_frame,
            text="⚙️",
            font=ctk.CTkFont(size=16),
        )
        settings_label.pack(side="left", padx=5)

        # Если профиля нет, показать экран создания профиля
        if not profile or not profile.get("name"):
            self._show_create_profile()
            return

        # ========== ГЛАВНЫЙ КОНТЕНТ ==========
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)

        # ========== ЦЕНТРАЛЬНАЯ КАРТОЧКА ==========
        card_frame = ctk.CTkFrame(
            content_frame,
            fg_color="#2B2B2B",
            corner_radius=25,
            border_color="#FFD700",
            border_width=2,
        )
        card_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Вся логика карточки внутри
        self._build_card_content(card_frame, profile)

        # ========== НИЖНЯЯ КНОПКА ==========
        back_btn = ctk.CTkButton(
            self,
            text="< BACK TO MAIN MENU",
            fg_color="transparent",
            border_color="#FFD700",
            border_width=2,
            text_color="#ffffff",
            font=ctk.CTkFont(size=12),
            command=lambda: self.app.switch_frame(MainMenuFrame),
            hover_color="#1a4d80",
        )
        back_btn.grid(row=2, column=0, sticky="w", padx=20, pady=15)

    def _build_card_content(self, card_frame: ctk.CTkFrame, profile: dict) -> None:
        """Построить содержимое центральной карточки."""

        # ========== ЗАГОЛОВОК (Аватар + Имя/Звание) ==========
        header_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(20, 15))

        # Аватар
        avatar_label = ctk.CTkLabel(
            header_frame,
            text="👤",
            font=ctk.CTkFont(size=70),
            text_color="#FFD700",
        )
        avatar_label.pack(side="left", padx=(0, 20))

        # Контейнер для имени и звания
        info_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True)

        # Имя
        player_name_label = ctk.CTkLabel(
            info_frame,
            text=f"PLAYER: {profile.get('name', 'Unknown').upper()}",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#ffffff",
            anchor="w",
        )
        player_name_label.pack(anchor="w")

        # Звание
        iq_score = profile.get("iq_score", 0)
        iq = 70 + iq_score
        iq = max(70, min(200, iq))
        title = self.app.data_manager.get_title(iq, profile.get("max_score", 0))

        # Определить цвет звания
        if title == "Новичок":
            rank_color = "#ffffff"  # белый
        elif title == "Эрудит":
            rank_color = "#1e90ff"  # синий
        elif title in ["Магистр", "Академик", "Миллионер"]:
            rank_color = "#FFD700"  # золотой
        else:
            rank_color = "#FFD700"  # для некоторых используем золотой по умолчанию

        rank_label = ctk.CTkLabel(
            info_frame,
            text=f"CURRENT RANK: {title}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=rank_color,
            anchor="w",
        )
        rank_label.pack(anchor="w", pady=(5, 0))

        # ========== ДВЕ КОЛОНКИ СТАТИСТИКИ ==========
        stats_container = ctk.CTkFrame(card_frame, fg_color="transparent")
        stats_container.pack(fill="x", padx=20, pady=(10, 20))

        # Левая колонка: Game IQ
        iq_box = ctk.CTkFrame(stats_container, fg_color="#1a1a1a", corner_radius=10)
        iq_box.pack(side="left", fill="both", expand=True, padx=(0, 10))

        iq_heading = ctk.CTkLabel(
            iq_box,
            text="GAME IQ",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
        )
        iq_heading.pack(padx=15, pady=(15, 5), anchor="w")

        iq_value = ctk.CTkLabel(
            iq_box,
            text=f"{int(iq)}",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#FFD700",
        )
        iq_value.pack(padx=15, pady=(0, 5))

        iq_subtitle = ctk.CTkLabel(
            iq_box,
            text=f"(Base IQ: 70 + {int(iq_score)} Bonus)",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w",
        )
        iq_subtitle.pack(padx=15, pady=(0, 15), anchor="w")

        # Правая колонка: Answer Accuracy
        accuracy_box = ctk.CTkFrame(stats_container, fg_color="#1a1a1a", corner_radius=10)
        accuracy_box.pack(side="left", fill="both", expand=True, padx=(10, 0))

        accuracy_heading = ctk.CTkLabel(
            accuracy_box,
            text="ANSWER ACCURACY",
            font=ctk.CTkFont(size=11),
            text_color="#888888",
            anchor="w",
        )
        accuracy_heading.pack(padx=15, pady=(15, 5), anchor="w")

        total_questions = profile.get("total_questions_answered", 0)
        total_correct = profile.get("total_correct_answers", 0)
        if total_questions > 0:
            accuracy = (total_correct / total_questions) * 100
        else:
            accuracy = 0

        accuracy_value = ctk.CTkLabel(
            accuracy_box,
            text=f"{accuracy:.0f}%",
            font=ctk.CTkFont(size=42, weight="bold"),
            text_color="#ffffff",
        )
        accuracy_value.pack(padx=15, pady=(0, 10))

        # Прогресс-бар
        progress_bar = ctk.CTkProgressBar(
            accuracy_box,
            width=200,
            height=14,
            progress_color="#00FF00",
            fg_color="#0a3d7a",
        )
        progress_bar.pack(padx=15, pady=(0, 8))
        progress_bar.set(accuracy / 100)

        accuracy_subtitle = ctk.CTkLabel(
            accuracy_box,
            text=f"Questions: {total_correct} / {total_questions} correct",
            font=ctk.CTkFont(size=10),
            text_color="#888888",
            anchor="w",
        )
        accuracy_subtitle.pack(padx=15, pady=(0, 15), anchor="w")

        # ========== RANKING PROGRESSION ==========
        ranking_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        ranking_frame.pack(fill="x", padx=20, pady=(20, 20))

        ranks = ["Novice", "Student", "Intellectual", "Erudite", "Master", "Academician", "Millionaire"]
        rank_values = [70, 85, 105, 125, 150, 180, 1000000]

        # Определить текущее звание по индексу
        current_rank_idx = 0
        for idx, (rank_name, rank_val) in enumerate(zip(ranks, rank_values)):
            if rank_name == "Millionaire" and profile.get("max_score", 0) >= 1000000:
                current_rank_idx = idx
                break
            elif rank_name != "Millionaire" and iq >= rank_val:
                current_rank_idx = idx

        # Визуализация шкалы
        rank_visual = ctk.CTkLabel(
            ranking_frame,
            text="●" + "─" * 65 + "●",
            font=ctk.CTkFont(size=10),
            text_color="#FFD700",
        )
        rank_visual.pack(pady=(0, 10))

        # Названия рангов
        ranks_text = ""
        for idx, rank_name in enumerate(ranks):
            if idx == current_rank_idx:
                ranks_text += f"[{rank_name}]"
            else:
                ranks_text += f"{rank_name}"
            if idx < len(ranks) - 1:
                ranks_text += "   "

        ranks_label = ctk.CTkLabel(
            ranking_frame,
            text=ranks_text,
            font=ctk.CTkFont(size=9),
            text_color="#FFD700",
        )
        ranks_label.pack()

        # ========== GAME LOG ==========
        log_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
        log_frame.pack(fill="x", padx=20, pady=(0, 20))

        log_heading = ctk.CTkLabel(
            log_frame,
            text="GAME LOG (Current Session)",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#cccccc",
            anchor="w",
        )
        log_heading.pack(anchor="w", pady=(0, 10))

        # Получить записи о последних ответах (если есть такие данные)
        # На данный момент будут показаны примерные записи
        log_entries = [
            ("Q14", "CORRECT", "+7 IQ", "#00FF00"),
            ("Q13", "CORRECT", "+7 IQ", "#00FF00"),
            ("Q12", "INCORRECT", "-2 IQ", "#FF6B6B"),
        ]

        for question_num, status, change, color in log_entries:
            log_line = ctk.CTkLabel(
                log_frame,
                text=f"{question_num}: {status} {change}",
                font=ctk.CTkFont(size=10),
                text_color=color,
                anchor="w",
            )
            log_line.pack(anchor="w", pady=1)

    def _show_create_profile(self) -> None:
        """Показать экран создания профиля."""
        # Верхняя часть: заголовок и иконка
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=(30, 20))

        icon_label = ctk.CTkLabel(
            header_frame,
            text="👤",
            font=ctk.CTkFont(size=60),
            text_color="#ffd700",
        )
        icon_label.pack()

        title_label = ctk.CTkLabel(
            header_frame,
            text="ПРОФИЛЬ ИГРОКА",
            font=ctk.CTkFont(family=FONTS.get("ladder", "Arial"), size=24, weight="bold"),
            text_color="#ffd700",
        )
        title_label.pack(pady=(10, 0))

        # Создание профиля (если нет)
        prompt_label = ctk.CTkLabel(
            self,
            text="Введите ваше имя:",
            font=ctk.CTkFont(size=18),
            text_color="#ffffff",
        )
        prompt_label.pack(pady=(30, 10))

        self.name_entry = ctk.CTkEntry(
            self,
            placeholder_text="Имя игрока",
            width=250,
            font=ctk.CTkFont(size=16),
        )
        self.name_entry.pack(pady=(0, 20))

        create_btn = ctk.CTkButton(
            self,
            text="Создать профиль",
            command=self._create_profile,
            fg_color="#0d5ecd",
            hover_color="#1a75ff",
        )
        create_btn.pack(pady=(0, 20))

        # Кнопка Назад
        back_btn = ctk.CTkButton(
            self,
            text="Назад",
            fg_color="#10233f",
            hover_color="#1a3b66",
            command=lambda: self.app.switch_frame(MainMenuFrame),
        )
        back_btn.pack(pady=(20, 20))

    def _change_name(self) -> None:
        dialog = ctk.CTkInputDialog(text="Введите новое имя:", title="Изменить имя")
        new_name = dialog.get_input()
        if new_name and new_name.strip():
            profile = self.app.data_manager.get_profile() or {}
            profile["name"] = new_name.strip()
            with open("profile.json", 'w', encoding='utf-8') as f:
                json.dump(profile, f, ensure_ascii=False, indent=4)
            # Перезагрузить фрейм
            self.app.switch_frame(ProfileFrame)

    def _create_profile(self) -> None:
        name = self.name_entry.get().strip()
        if name:
            self.app.data_manager.create_profile(name)
            self.app.switch_frame(ProfileFrame)


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
        self.lifeline_frame: Optional[ctk.CTkFrame] = None
        self.main_frame: Optional[ctk.CTkFrame] = None
        self.sidebar_frame: Optional[ctk.CTkFrame] = None
        self.current_frame: Optional[ctk.CTkFrame] = None

        # Сетка окна: центральная область + нижняя панель
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, columnspan=3, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        self.nav_frame = ctk.CTkFrame(self, fg_color="#020b23")
        self.nav_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        self.nav_frame.grid_columnconfigure(0, weight=1)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        self.nav_frame.grid_columnconfigure(2, weight=1)
        self.nav_frame.grid_columnconfigure(3, weight=1)

        self._build_nav_bar()

        # Показать главное меню
        self.show_main_menu()

    def _clear_current_frame(self) -> None:
        if self.current_frame is not None:
            if self.current_frame is self.menu_frame:
                self.menu_frame = None
            self.current_frame.destroy()
            self.current_frame = None

    def _build_nav_bar(self) -> None:
        nav_buttons = [
            ("Профиль", self.show_profile_window),
            ("Рекорды", self.show_records),
            ("Настройки", self.show_settings_window),
            ("Выход", self.destroy),
        ]

        for idx, (text, command) in enumerate(nav_buttons):
            btn = ctk.CTkButton(
                self.nav_frame,
                text=text,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#10233f",
                hover_color="#1a3b66",
                corner_radius=0,
                border_width=0,
                command=command,
            )
            btn.grid(row=0, column=idx, sticky="nsew", padx=1, pady=5)

    def switch_frame(self, frame_class, *args, **kwargs) -> None:
        self._clear_current_frame()
        self.current_frame = frame_class(self.content_frame, self, *args, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")
        self.nav_frame.grid()

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

        self.nav_frame.grid()
        self.switch_frame(MainMenuFrame)

        self.menu_frame = self.current_frame

    def start_game(self) -> None:
        if self.menu_frame is not None:
            self.menu_frame.destroy()
            self.menu_frame = None
        self._clear_current_frame()
        self.nav_frame.grid_remove()

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

        # Получить уровень вопроса
        level = self.engine.current_level + 1

        # Обновить статистику правильных ответов и IQ
        self.data_manager.update_correct_answers(is_correct, level)

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
        self.nav_frame.grid()
        self.switch_frame(ProfileFrame)

    # ---------- Окно настроек ----------

    def show_settings_window(self) -> None:
        self.nav_frame.grid()
        self.switch_frame(SettingsFrame)

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
        self.nav_frame.grid()
        self.switch_frame(RecordsFrame)

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
