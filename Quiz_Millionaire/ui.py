import customtkinter as ctk
from typing import Optional
from logic import QuizEngine
import os
import threading
from data_handler import DataManager
from sound_manager import SoundManager
import json
from localization import STRINGS
from PIL import Image

# Тёмная тема
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

def load_fonts():
    """Проверяет наличие .ttf файлов в папке /assets/fonts/ и регистрирует их.
    Если файлов нет, использует стандартные системные аналоги."""
    fonts_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")

    # Prefer Rubik.ttf as a primary font (supports Kyrgyz Cyrillic).
    rubik_path = os.path.join(fonts_dir, "Rubik.ttf")
    if os.path.exists(rubik_path):
        # Register font at runtime (Windows) so Kyrgyz Cyrillic renders correctly.
        # If this call fails, Tk will still fall back to default fonts.
        try:
            import ctypes

            ctypes.windll.gdi32.AddFontResourceExW(str(rubik_path), 0, None)
        except Exception:
            pass
        # We use the font family name "Rubik". If the system can't resolve it,
        # CTk will fall back to a default font (so text still remains readable).
        return {
            "question": "Rubik",
            "ladder": "Rubik",
            "number": "Rubik",
        }
    
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
        super().__init__(parent, fg_color="transparent")
        self.app = app

        # Directory and file paths
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
        bg_path = os.path.join(assets_dir, "main_bg.png.png")
        btn_path = os.path.join(assets_dir, "button_2.png.png")

        # Load raw PIL images
        self.bg_image_pil = Image.open(bg_path).convert("RGBA")
        self.btn_image_pil = Image.open(btn_path).convert("RGBA")

        # Configure grid FIRST with proper spanning for background
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.grid_rowconfigure(0, weight=2) # Top space / Title
        self.grid_rowconfigure(1, weight=1) # Main button
        self.grid_rowconfigure(2, weight=1) # Bottom buttons
        self.grid_rowconfigure(3, weight=1) # Bottom margin

        # Base CTkImage for background - created FIRST to sit at bottom
        self.bg_ctk_image = ctk.CTkImage(light_image=self.bg_image_pil, dark_image=self.bg_image_pil, size=(1280, 720))
        
        # Background label spanning all rows and columns using grid
        self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
        self.bg_label.grid(row=0, column=0, columnspan=10, rowspan=10, sticky="nsew")

        # Resize event tracking
        self._resize_timer = None
        self.bind("<Configure>", self._on_resize)

        # Game Title directly on self
        title_label = ctk.CTkLabel(
            self,
            text="КТО ХОЧЕТ СТАТЬ МИЛЛИОНЕРОМ?",
            font=ctk.CTkFont(family="Playfair Display SC", size=32, weight="bold"),
            text_color="#C9A92B",
            fg_color="transparent",
            bg_color="transparent"
        )
        title_label.grid(row=0, column=0, columnspan=3, sticky="n", pady=(100, 0))

        # Button Images stored as class attributes to prevent garbage collection
        self.btn_img_main = ctk.CTkImage(light_image=self.btn_image_pil, dark_image=self.btn_image_pil, size=(320, 80))
        self.btn_img_sub = ctk.CTkImage(light_image=self.btn_image_pil, dark_image=self.btn_image_pil, size=(260, 65))

        # Main Start Button
        self.start_button = ctk.CTkLabel(
            master=self.bg_label,
            image=self.btn_img_main,
            text="НАЧАТЬ ИГРУ",
            compound="center",
            font=ctk.CTkFont(family="Playfair Display SC", size=18, weight="bold"),
            text_color="#C9A92B",
            fg_color="transparent",
            bg_color="transparent",
            width=320,
            height=80,
            cursor="hand2"
        )
        self.start_button.place(relx=0.5, rely=0.72, anchor="center")
        self.start_button.bind("<Button-1>", lambda event: self.app.start_game())

        # Profile Button
        self.profile_button = ctk.CTkLabel(
            master=self.bg_label,
            image=self.btn_img_sub,
            text="Профиль",
            compound="center",
            font=ctk.CTkFont(family="Playfair Display SC", size=18, weight="bold"),
            text_color="#C9A92B",
            fg_color="transparent",
            bg_color="transparent",
            width=260,
            height=65,
            cursor="hand2"
        )
        self.profile_button.place(relx=0.18, rely=0.85, anchor="center")
        self.profile_button.bind("<Button-1>", lambda event: self.app.show_profile_window())

        # Settings Button
        self.settings_button = ctk.CTkLabel(
            master=self.bg_label,
            image=self.btn_img_sub,
            text="Настройки",
            compound="center",
            font=ctk.CTkFont(family="Playfair Display SC", size=18, weight="bold"),
            text_color="#C9A92B",
            fg_color="transparent",
            bg_color="transparent",
            width=260,
            height=65,
            cursor="hand2"
        )
        self.settings_button.place(relx=0.82, rely=0.85, anchor="center")
        self.settings_button.bind("<Button-1>", lambda event: self.app.show_settings_window())

    def _on_resize(self, event):
        # We only want to resize when the frame itself resizes, not its children
        if event.widget == self:
            if self._resize_timer is not None:
                self.after_cancel(self._resize_timer)
            self._resize_timer = self.after(100, lambda: self._do_resize(event.width, event.height))

    def _do_resize(self, w, h):
        if w > 50 and h > 50:
            try:
                self.bg_ctk_image = ctk.CTkImage(light_image=self.bg_image_pil, dark_image=self.bg_image_pil, size=(w, h))
                self.bg_label.configure(image=self.bg_ctk_image)
            except Exception:
                pass


class SettingsFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="transparent")
        self.app = app
        # --- Background Image ---
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
        bg_path = os.path.join(assets_dir, "main_bg.png.png")
        if os.path.exists(bg_path):
            self.bg_image_pil = Image.open(bg_path).convert("RGBA")
            self.bg_ctk_image = ctk.CTkImage(light_image=self.bg_image_pil, dark_image=self.bg_image_pil, size=(1280, 720))
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Centered container frame
        self.main_container = ctk.CTkFrame(
            self, 
            fg_color="#411A60",
            border_color="#B59341", 
            border_width=2,
            corner_radius=15
        )
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.6, relheight=0.7)

        # Back button in the top-left
        self.back_btn = ctk.CTkButton(
            self.main_container,
            text="←",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=40,
            height=40,
            corner_radius=15,
            border_width=1.5,
            border_color="#B59341",
            fg_color="transparent",
            bg_color="transparent",
            text_color="#E0C37B",
            hover_color="#592584",
            command=self.app.show_main_menu
        )
        self.back_btn.place(x=20, y=20)

        # Заголовок
        title_label = ctk.CTkLabel(
            self.main_container,
            text=self.app.tr("settings.title"),
            font=ctk.CTkFont(family="Playfair Display SC", size=26),
            text_color="#E0C37B",
        )
        title_label.pack(pady=(30, 40))

        content_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=80, pady=(0, 30))
        content_frame.grid_columnconfigure(0, weight=1, minsize=150)
        content_frame.grid_columnconfigure(1, weight=3)

        # 1. Громкость (Master)
        master_label = ctk.CTkLabel(
            content_frame,
            text=self.app.tr("settings.volume"),
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
            anchor="w"
        )
        master_label.grid(row=0, column=0, pady=15, sticky="w")

        self.master_slider = ctk.CTkSlider(
            content_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            height=12,
            progress_color="#E5C158",
            fg_color="#1C062E",
            button_color="#E5C158",
            button_hover_color="#fff2aa",
            command=lambda v: self._set_master_volume(float(v)),
        )
        self.master_slider.grid(row=0, column=1, pady=15, sticky="ew")

        # 2. Музыка
        music_label = ctk.CTkLabel(
            content_frame,
            text=self.app.tr("settings.music"),
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
            anchor="w"
        )
        music_label.grid(row=1, column=0, pady=15, sticky="w")

        self.music_slider = ctk.CTkSlider(
            content_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=100,
            height=12,
            progress_color="#E5C158",
            fg_color="#1C062E",
            button_color="#E5C158",
            button_hover_color="#fff2aa",
            command=lambda v: self._set_music_volume(float(v)),
        )
        self.music_slider.grid(row=1, column=1, pady=15, sticky="ew")

        # Таймер в игре
        timer_label = ctk.CTkLabel(
            content_frame,
            text=self.app.tr("settings.timer_in_game"),
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
            anchor="w"
        )
        timer_label.grid(row=2, column=0, pady=15, sticky="w")
        
        self.timer_switch = ctk.CTkSwitch(
            content_frame,
            text="",
            progress_color="#E5C158",
            fg_color="#1C062E",
            button_color="#E0C37B",
            button_hover_color="#fff2aa",
            command=self._toggle_timer,
        )
        self.timer_switch.grid(row=2, column=1, pady=15, sticky="w")

        # 3. Языки
        lang_title = ctk.CTkLabel(
            content_frame,
            text=self.app.tr("settings.language") + ":",
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
            anchor="nw"
        )
        lang_title.grid(row=3, column=0, pady=15, sticky="nw")

        lang_btns = ctk.CTkFrame(content_frame, fg_color="transparent")
        lang_btns.grid(row=3, column=1, pady=5, sticky="nsew")
        lang_btns.grid_columnconfigure(0, weight=1)

        btn_cfg = dict(
            font=ctk.CTkFont(family="Playfair Display SC", size=16),
            width=200,
            height=35,
            fg_color="#2E1045",
            hover_color="#592584",
            text_color="#E0C37B",
            corner_radius=12,
            border_width=1.5,
            border_color="#B59341"
        )

        ctk.CTkButton(lang_btns, text=self.app.tr("settings.language_ru"), command=lambda: self.app.set_language("ru"), **btn_cfg).pack(pady=6)
        ctk.CTkButton(lang_btns, text=self.app.tr("settings.language_en"), command=lambda: self.app.set_language("en"), **btn_cfg).pack(pady=6)
        ctk.CTkButton(lang_btns, text=self.app.tr("settings.language_ky"), command=lambda: self.app.set_language("ky"), **btn_cfg).pack(pady=6)

        # Загрузить настройки
        self._load_settings()

    def _load_settings(self) -> None:
        settings = self.app.data_manager.get_settings()
        master_vol = settings.get("master_volume", 1.0)
        music_vol = settings.get("music_volume", 0.5)
        timer = settings.get("timer_in_game", True)

        self.master_slider.set(master_vol)
        self.music_slider.set(music_vol)
        self.timer_switch.select() if timer else self.timer_switch.deselect()

        self.app.sound_manager.set_master_volume(master_vol)
        self.app.sound_manager.set_music_volume(music_vol)

    def _set_master_volume(self, value: float) -> None:
        self.app.sound_manager.set_master_volume(value)
        self._save_settings()

    def _set_music_volume(self, value: float) -> None:
        self.app.sound_manager.set_music_volume(value)
        self._save_settings()

    def _toggle_timer(self) -> None:
        self._save_settings()

    def _save_settings(self) -> None:
        settings = {
            "master_volume": self.master_slider.get(),
            "music_volume": self.music_slider.get(),
            "timer_in_game": self.timer_switch.get(),
        }
        self.app.data_manager.save_settings(settings)


class ProfileFrame(ctk.CTkFrame):
    def __init__(self, parent, app: "QuizApp") -> None:
        super().__init__(parent, fg_color="transparent")
        self.app = app
        
        # Initialize database manager
        from database import DatabaseManager
        self.db_manager = app.db_manager

        # --- Background Image ---
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
        bg_path = os.path.join(assets_dir, "main_bg.png.png")
        if os.path.exists(bg_path):
            self.bg_image_pil = Image.open(bg_path).convert("RGBA")
            self.bg_ctk_image = ctk.CTkImage(light_image=self.bg_image_pil, dark_image=self.bg_image_pil, size=(1280, 720))
            self.bg_label = ctk.CTkLabel(self, text="", image=self.bg_ctk_image)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # Centered container frame for the profile card
        self.main_container = ctk.CTkFrame(
            self, 
            fg_color="#411A60",
            border_color="#B59341", 
            border_width=2,
            corner_radius=15
        )
        self.main_container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_columnconfigure(1, weight=1)
        self.main_container.grid_rowconfigure(0, weight=0)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Заголовок раздела - Центрирован по всей ширине
        profile_title = ctk.CTkLabel(
            self.main_container,
            text=self.app.tr("profile.title"),
            font=ctk.CTkFont(family="Playfair Display SC", size=26),
            text_color="#E0C37B"
        )
        profile_title.grid(row=0, column=0, columnspan=2, pady=(30, 10), sticky="ew")

        # --- ЛЕВАЯ ПАНЕЛЬ (Статистика) ---
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_panel.grid(row=1, column=0, padx=(20, 10), pady=(5, 20), sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        self.left_panel.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=0)


        # Аватар
        self.avatar_label = ctk.CTkLabel(self.left_panel, text="👤", font=ctk.CTkFont(size=80), text_color="#A0A0A0")
        self.avatar_label.grid(row=0, column=0, pady=(20, 10), padx=20, sticky="w")

        # Имя и Ранг - теперь прижаты влево
        self.name_label = ctk.CTkLabel(
            self.left_panel, 
            text=f"{self.app.tr('profile.player_label')}: RUS",
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
            anchor="w"
        )
        self.name_label.grid(row=2, column=0, padx=30, pady=2, sticky="ew")

        # Dynamic rank display
        current_rank = self.app.data_manager.get_current_rank()
        rank_data = self.app.data_manager.get_rank_data()
        rank_info = rank_data.get(current_rank, {"icon": "🎯", "description": "Новичок"})
        
        self.rank_frame = ctk.CTkFrame(self.left_panel, fg_color="#2E1045", border_color="#B59341", border_width=1.5, corner_radius=10)
        self.rank_frame.grid(row=3, column=0, padx=30, pady=(2, 20), sticky="w")
        
        self.rank_label = ctk.CTkLabel(
            self.rank_frame, 
            text=f"{rank_info['icon']} {self.app.tr('profile.rank_label', rank=current_rank)}",
            font=ctk.CTkFont(family="Playfair Display SC", size=16),
            text_color="#E0C37B",
            anchor="w"
        )
        self.rank_label.pack(padx=15, pady=5)

        # СТАТИСТИКА - Заголовок по центру
        stats_title = ctk.CTkLabel(
            self.left_panel,
            text=self.app.tr("profile.stats_title"),
            font=ctk.CTkFont(family="Playfair Display SC", size=18),
            text_color="#E0C37B"
        )
        stats_title.grid(row=4, column=0, pady=(10, 10), padx=20, sticky="w")

        stats = self.app.data_manager.get_statistics()
        game_iq = stats["game_iq"]
        iq_label = ctk.CTkLabel(
            self.left_panel,
            text=f"Game IQ: {game_iq}/200",
            font=ctk.CTkFont(family="Playfair Display SC", size=20),
            text_color="#E0C37B",
        )
        iq_label.grid(row=5, column=0, pady=(10, 0), padx=20, sticky="w")  

        iq_progress = ctk.CTkProgressBar(
            self.left_panel,
            width=288,
            height=12,
            progress_color="#E5C158",
            fg_color="#1C062E",
        )
        iq_progress.grid(row=6, column=0, pady=(0, 20), padx=20, sticky="ew")  
        iq_progress.set(game_iq / 200)  

        # FORCE RELOAD: Get fresh stats from JSON (no caching!)
        self.app.data_manager._load_stats_from_json()
        
        # Use global variables directly for accuracy calculation
        total_q = self.app.data_manager.total_questions
        correct_q = self.app.data_manager.correct_answers
        
        # Calculate accuracy using (correct / total) with proper check
        if total_q > 0:
            accuracy = (correct_q / total_q) * 100
        else:
            accuracy = 0.0
        
                
        accuracy_label = ctk.CTkLabel(
            self.left_panel,
            text=self.app.tr("profile.accuracy", acc=accuracy),
            font=ctk.CTkFont(family="Playfair Display SC", size=18),
            text_color="#E0C37B",
        )
        accuracy_label.grid(row=7, column=0, pady=(0, 5), padx=20, sticky="w")  # Left-aligned  

        accuracy_progress = ctk.CTkProgressBar(
            self.left_panel,
            width=288,
            height=12,
            progress_color="#E5C158",
            fg_color="#1C062E",
        )
        accuracy_progress.grid(row=8, column=0, pady=(0, 20), padx=20, sticky="ew")  
        
        # Ensure progress bar gets float value between 0.0 and 1.0
        accuracy_float = float(accuracy) / 100.0
        accuracy_progress.set(accuracy_float)
                
          

        # --- ПРАВАЯ ПАНЕЛЬ (Рекорды и Достижения) ---
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.right_panel.grid(row=1, column=1, padx=(10, 20), pady=(5, 20), sticky="nsew")
        self.right_panel.grid_columnconfigure(0, weight=1)
        self.right_panel.grid_rowconfigure(0, weight=1) # Content area takes full height

        # Tab buttons moved to top right of main container
        self.tabs_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tabs_frame.place(relx=0.96, y=30, anchor="ne")

        self.records_btn = ctk.CTkButton(
            self.tabs_frame,
            text=self.app.tr("profile.records_tab"),
            font=ctk.CTkFont(family="Playfair Display SC", size=16),
            width=140,
            height=35,
            fg_color="transparent",
            border_width=1.5,
            border_color="#B59341",
            text_color="#E0C37B",
            hover_color="#592584",
            corner_radius=15,
            command=lambda: self._switch_to_records()
        )
        self.records_btn.grid(row=0, column=0, padx=(0, 5))

        self.achievements_btn = ctk.CTkButton(
            self.tabs_frame,
            text=self.app.tr("profile.achievements_tab"),
            font=ctk.CTkFont(family="Playfair Display SC", size=16),
            width=140,
            height=35,
            fg_color="transparent",
            border_width=1.5,
            border_color="#B59341",
            text_color="#E0C37B",
            hover_color="#592584",
            corner_radius=15,
            command=lambda: self._switch_to_achievements()
        )
        self.achievements_btn.grid(row=0, column=1, padx=(5, 0))

        # Контентная область для переключения
        self.content_area = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.content_area.grid(row=0, column=0, sticky="nsew", padx=20, pady=10)
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.show_records() # По умолчанию открываем рекорды

        # Back button in the top-left (placed last to guarantee it renders on the topmost layer)
        self.back_btn = ctk.CTkButton(
            self.main_container,
            text="←",
            font=ctk.CTkFont(size=20, weight="bold"),
            width=40,
            height=40,
            corner_radius=15,
            border_width=1.5,
            border_color="#B59341",
            fg_color="transparent",
            bg_color="transparent",
            text_color="#E0C37B",
            hover_color="#592584",
            command=self.app.show_main_menu
        )
        self.back_btn.place(x=20, y=20)
        self.back_btn.lift()  # Force the button to the absolute top layer

    def _update_tab_styles(self, active_tab: str) -> None:
        """Update tab button styles based on active tab."""
        if active_tab == "records":
            self.records_btn.configure(fg_color="#592584")
            self.achievements_btn.configure(fg_color="transparent")
        elif active_tab == "achievements":
            self.achievements_btn.configure(fg_color="#592584")
            self.records_btn.configure(fg_color="transparent")

    def _switch_to_records(self) -> None:
        """Switch to Records tab with proper highlighting."""
        self.refresh_data()
        self.show_records()
        self._update_tab_styles("records")

    def _switch_to_achievements(self) -> None:
        """Switch to Achievements tab with proper highlighting."""
        self.refresh_data()
        self.show_achievements()
        self._update_tab_styles("achievements")

    def refresh_records(self) -> None:
        """Force refresh the records display with latest data."""
        self.show_records()
    
    def refresh_data(self) -> None:
        """Re-open profile.json and read fresh numbers before drawing progress bars."""
        try:
            # Force reload profile from disk
            self.app.data_manager.force_save_to_disk(self.app.data_manager.get_profile() or {})
            
            # Rebuild left panel with fresh stats
            self._build_left_panel()
            
            # Refresh records display
            self.refresh_records()
            
        except Exception as e:
            pass
    
    def load_stats(self) -> None:
        """Load and refresh statistics for ProfileFrame."""
        try:
            # Rebuild left panel with updated stats
            self._build_left_panel()
        except Exception as e:
            print(f"Error loading stats: {e}")

    def show_records(self) -> None:
        """Show records content with professional table design."""
        try:
            print("DEBUG: Refreshing records display...")
            
            # Clear content area
            for widget in self.content_area.winfo_children():
                widget.destroy()
            
            # Create scrollable frame for records
            scrollable_frame = ctk.CTkScrollableFrame(
                self.content_area,
                fg_color="transparent",
                scrollbar_button_color="#592584",
                scrollbar_button_hover_color="#411A60",
                height=0
            )
            scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
            scrollable_frame.grid_columnconfigure(0, weight=1)
            
            # Records header + export buttons
            header_row = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
            header_row.grid(row=0, column=0, pady=(0, 15), padx=20, sticky="ew")
            header_row.grid_columnconfigure(0, weight=1)
            header_row.grid_columnconfigure((1, 2, 3, 4), weight=0)

            records_header = ctk.CTkLabel(
                header_row,
                text=self.app.tr("profile.records_header"),
                font=ctk.CTkFont(family="Playfair Display SC", size=16),
                text_color="#E0C37B",
            )
            records_header.grid(row=0, column=0, sticky="w")

            btn_cfg = dict(
                font=ctk.CTkFont(family="Playfair Display SC", size=12),
                width=70,
                height=32,
                corner_radius=10,
                border_width=1.5,
                border_color="#B59341",
                fg_color="transparent",
                hover_color="#592584",
                text_color="#E0C37B",
            )
            ctk.CTkButton(header_row, text="JSON", command=lambda: self._export_leaderboard("json"), **btn_cfg).grid(
                row=0, column=1, padx=(10, 0), sticky="e"
            )
            ctk.CTkButton(header_row, text="CSV", command=lambda: self._export_leaderboard("csv"), **btn_cfg).grid(
                row=0, column=2, padx=(8, 0), sticky="e"
            )
            ctk.CTkButton(header_row, text="EXCEL", command=lambda: self._export_leaderboard("excel"), **btn_cfg).grid(
                row=0, column=3, padx=(8, 0), sticky="e"
            )
            ctk.CTkButton(header_row, text="PDF", command=lambda: self._export_leaderboard("pdf"), **btn_cfg).grid(
                row=0, column=4, padx=(8, 0), sticky="e"
            )
            
            # FORCE RELOAD: Get fresh data from database (no caching!)
            print("DEBUG: Force reloading database connection...")
            top_records = self.db_manager.get_top_scores(limit=10)
            print(f"DEBUG: Retrieved {len(top_records)} records from database")
            
            if not top_records:
                empty_label = ctk.CTkLabel(
                    scrollable_frame,
                    text=self.app.tr("profile.records_empty"),
                    font=ctk.CTkFont(size=14),
                    text_color="#ffffff",
                )
                empty_label.grid(row=1, column=0, pady=20, padx=20, sticky="w")
            else:
                # Create table header row
                header_frame = ctk.CTkFrame(
                    scrollable_frame,
                    fg_color="#2E1045",
                    corner_radius=8,
                    border_color="#B59341",
                    border_width=1.5
                )
                header_frame.grid(row=1, column=0, pady=(0, 10), padx=20, sticky="ew")
                
                # Configure header columns
                header_frame.grid_columnconfigure(0, weight=0, minsize=40)  # Rank
                header_frame.grid_columnconfigure(1, weight=2, minsize=150)  # Name
                header_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Series
                header_frame.grid_columnconfigure(3, weight=1, minsize=80)   # Time
                header_frame.grid_columnconfigure(4, weight=1, minsize=120)  # Winnings
                
                # Header labels
                rank_header = ctk.CTkLabel(
                    header_frame,
                    text=self.app.tr("records_table.rank"),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#E0C37B",
                )
                rank_header.grid(row=0, column=0, padx=10, pady=8, sticky="w")
                
                name_header = ctk.CTkLabel(
                    header_frame,
                    text=self.app.tr("records_table.name"),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#E0C37B",
                )
                name_header.grid(row=0, column=1, padx=10, pady=8, sticky="w")
                
                series_header = ctk.CTkLabel(
                    header_frame,
                    text=self.app.tr("records_table.series"),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#E0C37B",
                )
                series_header.grid(row=0, column=2, padx=10, pady=8, sticky="")
                
                time_header = ctk.CTkLabel(
                    header_frame,
                    text=self.app.tr("records_table.time"),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#E0C37B",
                )
                time_header.grid(row=0, column=3, padx=10, pady=8, sticky="")
                
                winnings_header = ctk.CTkLabel(
                    header_frame,
                    text=self.app.tr("records_table.winnings"),
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color="#E0C37B",
                )
                winnings_header.grid(row=0, column=4, padx=10, pady=8, sticky="e")
                
                # Create data rows
                for i, record in enumerate(top_records, 1):
                    print(f"DEBUG: Displaying record {i}: {record['name']} - {record['score']} ₽")
                    
                    # Alternating row colors
                    row_color = "#3A1457" if i % 2 == 1 else "#451966"
                    
                    record_frame = ctk.CTkFrame(
                        scrollable_frame,
                        fg_color=row_color,
                        corner_radius=8,
                        border_color="#B59341",
                        border_width=1.5
                    )
                    record_frame.grid(row=i+1, column=0, pady=2, padx=20, sticky="ew")
                    
                    # Configure row columns
                    record_frame.grid_columnconfigure(0, weight=0, minsize=40)  # Rank
                    record_frame.grid_columnconfigure(1, weight=2, minsize=150)  # Name
                    record_frame.grid_columnconfigure(2, weight=1, minsize=100)  # Series
                    record_frame.grid_columnconfigure(3, weight=1, minsize=80)   # Time
                    record_frame.grid_columnconfigure(4, weight=1, minsize=120)  # Winnings
                    
                    # Rank number - highlight top 3 in gold
                    rank_color = "#ffd700" if i <= 3 else "#ffffff"
                    rank_label = ctk.CTkLabel(
                        record_frame,
                        text=str(i),
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color=rank_color,
                    )
                    rank_label.grid(row=0, column=0, padx=10, pady=6, sticky="w")
                    
                    # Player name - left aligned
                    name_label = ctk.CTkLabel(
                        record_frame,
                        text=record["name"],
                        font=ctk.CTkFont(size=12),
                        text_color="#ffffff",
                    )
                    name_label.grid(row=0, column=1, padx=10, pady=6, sticky="w")
                    
                    # Series (win streak) - centered as number
                    streak_value = record.get("rank", "0")
                    # Ensure we display a number, not a rank string
                    try:
                        streak_number = int(streak_value)
                        series_text = str(streak_number)
                    except (ValueError, TypeError):
                        series_text = "0"
                    
                    series_label = ctk.CTkLabel(
                        record_frame,
                        text=series_text,
                        font=ctk.CTkFont(size=12),
                        text_color="#cccccc",
                    )
                    series_label.grid(row=0, column=2, padx=10, pady=6, sticky="")
                    
                    # Time - centered
                    time_seconds = record.get("time_seconds", 0)
                    minutes = time_seconds // 60
                    seconds = time_seconds % 60
                    time_text = f"{minutes}:{seconds:02d}"
                    
                    time_label = ctk.CTkLabel(
                        record_frame,
                        text=time_text,
                        font=ctk.CTkFont(size=12),
                        text_color="#cccccc",
                    )
                    time_label.grid(row=0, column=3, padx=10, pady=6, sticky="")
                    
                    # Winnings - right aligned in gold
                    winnings_text = f"{record['score']:,} ₽"
                    winnings_label = ctk.CTkLabel(
                        record_frame,
                        text=winnings_text,
                        font=ctk.CTkFont(size=12, weight="bold"),
                        text_color="#ffd700",
                    )
                    winnings_label.grid(row=0, column=4, padx=10, pady=6, sticky="e")
                    
        except Exception as e:
            print(f"ERROR: Failed to display records: {e}")
            # Show error message
            error_label = ctk.CTkLabel(
                self.content_area,
                text=f"Ошибка загрузки рекордов: {e}",
                font=ctk.CTkFont(size=14),
                text_color="#ff0000",
            )
            error_label.grid(row=0, column=0, pady=20, padx=20, sticky="w")

    def _export_leaderboard(self, fmt: str) -> None:
        """Export Top-10 leaderboard without freezing UI."""
        fmt = (fmt or "").lower().strip()

        def worker() -> None:
            try:
                from exporter import DataExporter

                top_records = self.db_manager.get_top_scores(limit=10)
                exporter = DataExporter()

                if fmt == "json":
                    result = exporter.export_json(top_records)
                elif fmt == "csv":
                    result = exporter.export_csv(top_records)
                elif fmt == "excel":
                    result = exporter.export_excel(top_records)
                elif fmt == "pdf":
                    result = exporter.export_pdf(top_records)
                else:
                    raise ValueError(f"Unknown export format: {fmt}")

                self.after(0, lambda: self._notify_export_success(result.exports_dir))
            except Exception as e:
                self.after(0, lambda: self._notify_export_error(str(e)))

        threading.Thread(target=worker, daemon=True).start()

    def _notify_export_success(self, exports_dir: str) -> None:
        try:
            dialog = ctk.CTkToplevel(self)
            dialog.title(self.app.tr("dialogs.export.error_title"))
            dialog.geometry("360x140")
            dialog.attributes("-topmost", True)
            dialog.configure(fg_color="#020b23")

            ctk.CTkLabel(
                dialog,
                text=self.app.tr("dialogs.export.success"),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#00ff00",
            ).pack(pady=(25, 10))

            ctk.CTkButton(
                dialog,
                text=self.app.tr("dialogs.export.error_ok"),
                command=dialog.destroy,
                fg_color="#10233f",
                hover_color="#1a3b66",
                text_color="#ffd700",
            ).pack(pady=(0, 15))

            try:
                if os.name == "nt":
                    os.startfile(exports_dir)  # type: ignore[attr-defined]
                else:
                    import subprocess

                    subprocess.Popen(["xdg-open", exports_dir])
            except Exception:
                pass
        except Exception:
            pass

    def _notify_export_error(self, message: str) -> None:
        try:
            dialog = ctk.CTkToplevel(self)
            dialog.title(self.app.tr("dialogs.export.error_title"))
            dialog.geometry("520x180")
            dialog.attributes("-topmost", True)
            dialog.configure(fg_color="#020b23")

            ctk.CTkLabel(
                dialog,
                text=self.app.tr("dialogs.export.error_title"),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#ff0000",
            ).pack(pady=(20, 8))

            ctk.CTkLabel(
                dialog,
                text=message,
                font=ctk.CTkFont(size=12),
                text_color="#ffffff",
                wraplength=480,
                justify="left",
            ).pack(padx=20, pady=(0, 10))

            ctk.CTkButton(
                dialog,
                text=self.app.tr("dialogs.export.error_ok"),
                command=dialog.destroy,
                fg_color="#10233f",
                hover_color="#1a3b66",
                text_color="#ffd700",
            ).pack(pady=(0, 15))
        except Exception:
            pass

    def show_achievements(self) -> None:
        """Show achievements content."""
        # Clear content area
        for widget in self.content_area.winfo_children():
            widget.destroy()
        
        # Create scrollable frame for achievements - NO fixed height, let it expand
        scrollable_frame = ctk.CTkScrollableFrame(
            self.content_area,
            fg_color="transparent",
            scrollbar_button_color="#10233f",
            scrollbar_button_hover_color="#1a3b66",
            height=0  # Let it expand via grid configuration
        )
        scrollable_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        scrollable_frame.grid_columnconfigure(0, weight=1)
        
        # Get achievements data
        achievements_data = self.app.data_manager.get_achievements_data()
        achievements = achievements_data["achievements"]
        
        # Group achievements by category
        categories = {}
        for achievement_id, achievement in achievements.items():
            category = achievement["category"]
            if category not in categories:
                categories[category] = []
            categories[category].append(achievement)
        
        row = 0
        
        # Display achievements by category
        category_map = {
            "Путь к богатству": "achievement.category.wealth",
            "Работа с подсказками": "achievement.category.hints",
            "Сложные ситуации": "achievement.category.difficult",
            "Особые заслуги": "achievement.category.special"
        }
        
        for category_name, category_achievements in categories.items():
            # Category header
            localized_category = self.app.tr(category_map.get(category_name, category_name))
            category_header = ctk.CTkLabel(
                scrollable_frame,
                text=localized_category,
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#ffd700",
            )
            category_header.grid(row=row, column=0, pady=(15, 10), padx=20, sticky="w")
            row += 1
            
            # Achievement cards
            for achievement in category_achievements:
                # Achievement card frame
                card_frame = ctk.CTkFrame(
                    scrollable_frame,
                    fg_color="#10233f" if not achievement["is_unlocked"] else "#1a3b66",
                    border_color="#ffd700" if achievement["is_unlocked"] else "#555555",
                    border_width=2 if achievement["is_unlocked"] else 1,
                    corner_radius=10
                )
                card_frame.grid(row=row, column=0, pady=5, padx=20, sticky="ew")
                card_frame.grid_columnconfigure(0, weight=1)
                row += 1
                
                # Achievement content
                content_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                content_frame.grid(row=0, column=0, padx=15, pady=12, sticky="ew")
                content_frame.grid_columnconfigure(0, weight=1)
                content_frame.grid_columnconfigure(1, weight=0)
                
                # Localized Title and Status
                aid = achievement["id"]
                localized_title = self.app.tr(f"achievement.{aid}.title")
                localized_desc = self.app.tr(f"achievement.{aid}.desc")

                title_label = ctk.CTkLabel(
                    content_frame,
                    text=localized_title,
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="#ffd700" if achievement["is_unlocked"] else "#ffffff",
                    anchor="w"
                )
                title_label.grid(row=0, column=0, sticky="w")
                
                status_label = ctk.CTkLabel(
                    content_frame,
                    text="✓" if achievement["is_unlocked"] else "🔒",
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#00ff00" if achievement["is_unlocked"] else "#ff0000",
                )
                status_label.grid(row=0, column=1, padx=(10, 0), sticky="e")
                
                # Localized Description
                desc_label = ctk.CTkLabel(
                    content_frame,
                    text=localized_desc,
                    font=ctk.CTkFont(size=11),
                    text_color="#cccccc" if not achievement["is_unlocked"] else "#ffffff",
                    wraplength=320,
                    anchor="w",
                    justify="left"
                )
                desc_label.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="w")

class QuizApp(ctk.CTk):
    def __init__(self, engine: QuizEngine, sound_manager: Optional[SoundManager] = None) -> None:
        super().__init__()

        self.engine = engine
        self.data_manager = DataManager()
        self.sound_manager = sound_manager or SoundManager()
        
        # Initialize database manager
        from database import DatabaseManager
        self.db_manager = DatabaseManager()

        # Localization
        self._language: str = self._load_language_from_config()
        print(f"DEBUG: Current Language setting: [{self._language}]")
        self._strings: dict[str, str] = STRINGS.get(self._language, STRINGS["ru"])
        # Ensure engine has language if it supports it
        if hasattr(self.engine, "set_language"):
            try:
                self.engine.set_language(self._language)  # type: ignore[attr-defined]
            except Exception:
                pass
        
        # Game state flags
        self.game_over_active = False
        self._is_game_over_processed = False
        self._already_ended = False
        # Strict one-shot lock for any game-ending flow (loss/win/take-money/timeout)
        self._game_ending_processed = False
        # App closing guard (prevents double close/commit calls)
        self._app_closing = False
        
        # IMPORTANT: Do not delete or reset leaderboard on startup.

        # Graceful shutdown: commit -> close DB -> stop sound -> destroy
        self.protocol("WM_DELETE_WINDOW", self.safe_exit)

        self.prize_levels = []
        self.title("Кто хочет стать миллионером?")
        self.geometry("1200x700")
        self.resizable(True, True)

        # Bind F11 and Escape keys for responsive fullscreen mode toggles
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

        # Bind the window resizing event (<Configure>) to a dedicated dynamic resize handler method
        self.bind("<Configure>", self.resize_background)

        # Ensure window is visible and focused
        self.lift()
        self.focus_force()
        self.attributes("-topmost", True)
        self.after(100, lambda: self.attributes("-topmost", False))

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

        # Сетка окна: центральная область
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.grid(row=0, column=0, sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Показать главное меню
        self.show_main_menu()

    def toggle_fullscreen(self, event=None) -> str:
        is_fullscreen = not self.attributes("-fullscreen")
        self.attributes("-fullscreen", is_fullscreen)
        return "break"

    def exit_fullscreen(self, event=None) -> str:
        self.attributes("-fullscreen", False)
        return "break"

    def resize_background(self, event):
        # CRITICAL FIX: Only execute resizing if the event target is exactly the top-level app window
        if event.widget != self:
            return
            
        new_width = self.winfo_width()
        new_height = self.winfo_height()
        
        # Safeguard minimum glitch tracking sizes
        if new_width < 200 or new_height < 200:
            return
            
        # Safely update game screen background image ONLY if it exists and is active
        if hasattr(self, 'game_bg_ctk_image') and self.game_bg_ctk_image:
            try:
                self.game_bg_ctk_image.configure(size=(new_width, new_height))
            except Exception:
                pass
                
        # Safely update active frame's background image ONLY if the frame is currently rendered
        if hasattr(self, 'current_frame') and self.current_frame:
            if hasattr(self.current_frame, 'bg_ctk_image') and self.current_frame.bg_ctk_image:
                try:
                    self.current_frame.bg_ctk_image.configure(size=(new_width, new_height))
                except Exception:
                    pass

    def safe_exit(self) -> None:
        """Gracefully shutdown the app and persist data."""
        if getattr(self, "_app_closing", False):
            return
        self._app_closing = True

        # Stop active timers early to avoid callbacks firing during teardown
        try:
            if getattr(self, "_timer_id", None) is not None:
                try:
                    self.after_cancel(self._timer_id)
                except Exception:
                    pass
                self._timer_id = None
        except Exception:
            pass

        # Stop any music / sound first
        try:
            if getattr(self, "sound_manager", None) is not None:
                self.sound_manager.stop_bg_music()
        except Exception:
            pass

        # Final DB flush and close (only here)
        try:
            if getattr(self, "db_manager", None) is not None and getattr(self.db_manager, "conn", None) is not None:
                try:
                    self.db_manager.conn.commit()
                except Exception:
                    pass
                try:
                    self.db_manager.conn.close()
                except Exception:
                    pass
        except Exception:
            pass

        try:
            self.destroy()
        except Exception:
            pass

    # Backwards-compatible alias (older code may still call it)
    def on_app_close(self) -> None:
        self.safe_exit()

    # ---------- Localization ----------
    def _load_language_from_config(self) -> str:
        """Load selected UI language from config.json."""
        try:
            cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            if not os.path.exists(cfg_path):
                return "ru"
            with open(cfg_path, "r", encoding="utf-8") as f:
                cfg = json.load(f)
            lang = (cfg.get("language") or "ru").strip().lower()
            if lang in STRINGS:
                return lang
            return "ru"
        except Exception:
            return "ru"

    def _save_language_to_config(self, lang: str) -> None:
        try:
            cfg_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
            with open(cfg_path, "w", encoding="utf-8") as f:
                json.dump({"language": lang}, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def tr(self, key: str, **kwargs) -> str:
        template = self._strings.get(key, STRINGS["ru"].get(key, key))
        try:
            return template.format(**kwargs)
        except Exception:
            return template

    def set_language(self, lang: str) -> None:
        lang = (lang or "").strip().lower()
        if lang not in STRINGS:
            lang = "ru"
        if lang == self._language:
            return
        self._language = lang
        print(f"DEBUG: Current Language setting: [{self._language}]")
        self._strings = STRINGS[lang]
        self._save_language_to_config(lang)
        
        # Immediately update engine language regardless of current screen
        if hasattr(self.engine, "set_language"):
            try:
                self.engine.set_language(self._language)
            except Exception:
                pass
        
        self.update_ui_text()

    def update_ui_text(self) -> None:
        """Rebuild visible screens to apply language changes instantly."""
        try:
            # Rebuild active frame (menu/settings/profile) using updated strings
            if isinstance(self.current_frame, SettingsFrame):
                self.show_settings_window()
                return
            if isinstance(self.current_frame, ProfileFrame):
                self.show_profile_window()
                return
            if isinstance(self.current_frame, MainMenuFrame) or self.current_frame is None:
                self.show_main_menu()
                return

            # In-game: update live labels and lifelines, then reload question.
            if self.current_question_data is not None:
                if hasattr(self.engine, "set_language"):
                    try:
                        self.engine.set_language(self._language)  # type: ignore[attr-defined]
                    except Exception:
                        pass

                # Update lifeline button captions immediately (panel already exists during game)
                try:
                    if getattr(self, "btn_5050", None) is not None:
                        self.btn_5050.configure(text=self.tr("lifeline.5050"))
                    if getattr(self, "btn_call_friend", None) is not None:
                        self.btn_call_friend.configure(text=self.tr("lifeline.call_friend"))
                    if getattr(self, "btn_audience", None) is not None:
                        self.btn_audience.configure(text=self.tr("lifeline.audience"))
                    if getattr(self, "btn_take_money", None) is not None:
                        self.btn_take_money.configure(text=self.tr("lifeline.take_money"))
                    if getattr(self, "btn_second_chance", None) is not None:
                        self.btn_second_chance.configure(text=self.tr("lifeline.second_chance"))
                except Exception:
                    pass

                # Reload current question set (language change can affect question text)
                try:
                    self.engine.prepare_new_game()
                except Exception:
                    pass
                self.current_question_data = None
                # Force UI refresh
                self.load_next_question()
        except Exception:
            pass

    def _clear_current_frame(self) -> None:
        if self.current_frame is not None:
            if self.current_frame is self.menu_frame:
                self.menu_frame = None
            self.current_frame.destroy()
            self.current_frame = None

    def switch_frame(self, frame_class, *args, **kwargs) -> None:
        self._clear_current_frame()

        self.current_frame = frame_class(self.content_frame, self, *args, **kwargs)
        self.current_frame.grid(row=0, column=0, sticky="nsew")

    # ---------- Главное меню ----------
    def show_main_menu(self) -> None:
        # Остановить текущую музыку и таймеры
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music("main_theme.mp3")
        
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

        if self.lifeline_frame is not None:
            try:
                self.lifeline_frame.destroy()
            except Exception:
                pass
            self.lifeline_frame = None
        if self.main_frame is not None:
            try:
                self.main_frame.destroy()
            except Exception:
                pass
            self.main_frame = None
        if self.sidebar_frame is not None:
            try:
                self.sidebar_frame.destroy()
            except Exception:
                pass
            self.sidebar_frame = None
        if getattr(self, "game_bg_label", None) is not None:
            try:
                self.game_bg_label.destroy()
            except Exception:
                pass
            self.game_bg_label = None

        self.switch_frame(MainMenuFrame)

        self.menu_frame = self.current_frame

    def start_game(self) -> None:
        if self.menu_frame is not None:
            self.menu_frame.destroy()
            self.menu_frame = None
        self._clear_current_frame()
        
        # Переход в игру — смена фоновой музыки
        self.sound_manager.stop_bg_music()
        self.sound_manager.play_bg_music("question_background.mp3")

        self.engine.prepare_new_game()
        self.is_processing = False
        self.current_question_data = None
        self.used_call_friend = False
        self.safety_net_active = False
        
        # Reset game over flag for new game
        self.game_over_active = False
        self._is_game_over_processed = False
        self._already_ended = False
        self._game_ending_processed = False

        # Track game start time for sprinter achievement and database time calculation
        import time
        self.start_time = time.time()
        self.data_manager.update_session_stats(game_start_time=self.start_time)
        print(f"DEBUG: Game start time set: {self.start_time}")
        
        # Initialize win streak tracking for this game session
        self.current_streak = 0
        self.max_streak_in_game = 0
        print(f"DEBUG: Win streak tracking initialized - Current: {self.current_streak}, Max: {self.max_streak_in_game}")

        # Set up fullscreen background image for gameplay (guaranteed to be instantiated)
        assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "images")
        bg_path = os.path.join(assets_dir, "main_bg.png.png")
        if os.path.exists(bg_path):
            from PIL import Image
            self.game_bg_image_pil = Image.open(bg_path).convert("RGBA")
            self.game_bg_ctk_image = ctk.CTkImage(light_image=self.game_bg_image_pil, dark_image=self.game_bg_image_pil, size=(1200, 700))
            self.game_bg_label = ctk.CTkLabel(self, text="", image=self.game_bg_ctk_image)
            self.game_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        else:
            self.game_bg_label = ctk.CTkLabel(self, text="", fg_color="#18072B")
            self.game_bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self._create_main_area()
        self._create_sidebar()

        self.load_next_question()

    def return_to_main_menu(self) -> None:
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        self.show_main_menu()

    # ---------- Игровые панели ----------

    def _create_lifeline_panel(self) -> None:
        pass

    def _create_main_area(self) -> None:
        # Home button in top-left directly on self.game_bg_label
        self.home_btn = ctk.CTkButton(
            self.game_bg_label,
            text="🏠",
            font=ctk.CTkFont(size=18),
            width=36,
            height=36,
            corner_radius=18,
            border_width=1.5,
            border_color="#ffffff",
            fg_color="#ffffff",
            text_color="#000000",
            hover_color="#e0e0e0",
            command=self.show_main_menu
        )
        self.home_btn.place(x=20, y=20)

        # Question counter in top-left next to home button
        self.counter_btn = ctk.CTkButton(
            self.game_bg_label,
            text="01/15",
            font=ctk.CTkFont(family="Arial", size=11, weight="bold"),
            width=50,
            height=36,
            corner_radius=18,
            border_width=1.5,
            border_color="#cccccc",
            fg_color="#ffffff",
            text_color="#000000",
            hover_color="#ffffff",
            state="normal"
        )
        self.counter_btn.place(x=70, y=20)

        # Invisible label attribute to avoid crashes from references elsewhere
        self.question_header_label = ctk.CTkLabel(self.game_bg_label, text="")

        # Golden ribbon line stretching across the left gameplay area
        self.ribbon_line = ctk.CTkFrame(
            self.game_bg_label,
            height=4,
            fg_color="#B59341",
            border_width=0
        )
        # self.ribbon_line.place(relx=0.38, rely=0.35, anchor="center", relwidth=0.76)

        # Centered Question Container Box
        self.question_container = ctk.CTkFrame(
            self.game_bg_label,
            fg_color="#2E1045",
            border_color="#B59341",
            border_width=2,
            corner_radius=35,
            height=120
        )
        self.question_container.place(relx=0.38, rely=0.45, anchor="center", relwidth=0.68)

        self.question_label = ctk.CTkLabel(
            self.question_container,
            text="",
            font=ctk.CTkFont(family=FONTS["question"], size=20, weight="bold"),
            wraplength=600,
            justify="center",
            fg_color="transparent",
            text_color="#E0C37B",
        )
        self.question_label.pack(expand=True, fill="both", padx=30, pady=20)

        self.timer_label = ctk.CTkLabel(
            self.game_bg_label,
            text="",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#ffffff",
            fg_color="transparent"
        )
        self.timer_label.place(relx=0.38, rely=0.58, anchor="center")

        self.answer_buttons = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.game_bg_label,
                text=f"{chr(ord('A') + i)}: ",
                font=ctk.CTkFont(family=FONTS["question"], size=16, weight="bold"),
                height=50,
                corner_radius=20,
                fg_color="#411A60",
                hover_color="#592584",
                text_color="#E5C158",
                border_width=1.5,
                border_color="#B59341",
                command=lambda idx=i: self.handle_click(idx),
            )
            # Place answer buttons in a perfect 2x2 grid in left area
            relx_val = 0.21 if i % 2 == 0 else 0.55
            rely_val = 0.68 if i // 2 == 0 else 0.79
            btn.place(relx=relx_val, rely=rely_val, relwidth=0.32, relheight=0.08, anchor="center")
            self.answer_buttons.append(btn)

    def _create_sidebar(self) -> None:
        # Lifeline buttons container directly on the game_bg_label
        self.lifeline_frame = ctk.CTkFrame(self.game_bg_label, fg_color="transparent")
        self.lifeline_frame.place(relx=0.90, rely=0.18, anchor="center", relwidth=0.18)
        
        cfg_call = {
            "width": 200,
            "height": 36,
            "corner_radius": 18,
            "fg_color": "#28C745",
            "hover_color": "#21a83a",
            "text_color": "#000000",
            "font": ctk.CTkFont(family="Arial", size=11, weight="bold"),
        }
        cfg_audience = {
            "width": 200,
            "height": 36,
            "corner_radius": 18,
            "fg_color": "#FFC107",
            "hover_color": "#e0a800",
            "text_color": "#000000",
            "font": ctk.CTkFont(family="Arial", size=11, weight="bold"),
        }
        cfg_5050 = {
            "width": 200,
            "height": 36,
            "corner_radius": 18,
            "fg_color": "#721C24",
            "hover_color": "#5c131a",
            "text_color": "#ffffff",
            "font": ctk.CTkFont(family="Arial", size=11, weight="bold"),
        }
        cfg_other = {
            "width": 200,
            "height": 32,
            "corner_radius": 16,
            "fg_color": "#10233f",
            "hover_color": "#1a3b66",
            "text_color": "#e6e6e6",
            "font": ctk.CTkFont(family="Arial", size=10, weight="bold"),
        }

        self.btn_call_friend = ctk.CTkButton(
            self.lifeline_frame,
            text=self.tr("lifeline.call_friend"),
            command=self._on_call_friend,
            **cfg_call
        )
        self.btn_call_friend.pack(pady=4, fill="x")

        self.btn_audience = ctk.CTkButton(
            self.lifeline_frame,
            text=self.tr("lifeline.audience"),
            command=self.use_hint_audience,
            **cfg_audience
        )
        self.btn_audience.pack(pady=4, fill="x")

        self.btn_5050 = ctk.CTkButton(
            self.lifeline_frame,
            text=self.tr("lifeline.5050"),
            command=self.use_hint_5050,
            **cfg_5050
        )
        self.btn_5050.pack(pady=4, fill="x")

        self.btn_take_money = ctk.CTkButton(
            self.lifeline_frame,
            text=self.tr("lifeline.take_money"),
            command=self._take_money,
            **cfg_other
        )
        self.btn_take_money.pack(pady=4, fill="x")

        self.btn_second_chance = ctk.CTkButton(
            self.lifeline_frame,
            text=self.tr("lifeline.second_chance"),
            command=self._on_second_chance,
            **cfg_other
        )
        self.btn_second_chance.pack(pady=4, fill="x")

        # Container for the ladder grid directly on the game_bg_label
        ladder_container = ctk.CTkFrame(self.game_bg_label, fg_color="transparent")
        ladder_container.place(relx=0.90, rely=0.62, anchor="center", relwidth=0.18, relheight=0.45)
        ladder_container.grid_columnconfigure(0, weight=1)

        self.prize_levels = [
            "500", "1,000", "1,500", "3,000", "7,500",
            "10,000", "25,000", "40,000", "70,000", "100,000",
            "250,000", "450,000", "750,000", "1,000,000", "1,500,000"
        ]

        self.prize_labels = []
        for i, amount in enumerate(reversed(self.prize_levels)):
            level_num = 15 - i
            
            # Configure row weight to force vertical stretching
            ladder_container.grid_rowconfigure(i, weight=1)
            
            # Row frame for highlight background - stretches to fill its grid cell
            row_frame = ctk.CTkFrame(ladder_container, fg_color="transparent", corner_radius=10)
            row_frame.grid(row=i, column=0, sticky="nsew", pady=1)
            row_frame.grid_propagate(False)
            
            # Two-column layout within the row
            row_frame.grid_columnconfigure(0, weight=1)  # Number
            row_frame.grid_columnconfigure(1, weight=3)  # Amount
            row_frame.grid_rowconfigure(0, weight=1)     # Center content vertically
            
            num_lbl = ctk.CTkLabel(
                row_frame,
                text=f"{level_num})",
                font=ctk.CTkFont(family=FONTS["ladder"], size=12),
                anchor="w",
                padx=10,
                text_color="#FFFFFF",
            )
            num_lbl.grid(row=0, column=0, sticky="nsew")
            
            amount_lbl = ctk.CTkLabel(
                row_frame,
                text=amount,
                font=ctk.CTkFont(family=FONTS["ladder"], size=12),
                anchor="e",
                padx=10,
                text_color="#FFFFFF",
            )
            amount_lbl.grid(row=0, column=1, sticky="nsew")
            
            # Store tuple of components for status updates
            self.prize_labels.append((num_lbl, amount_lbl, row_frame))

        self.update_money_ladder()

        # Close/Exit Button directly on the game_bg_label at the bottom of the sidebar
        close_text = self._strings.get("buttons.close") or self._strings.get("dialogs.exit.title") or "Закрыть"
        self.close_btn = ctk.CTkButton(
            self.game_bg_label,
            text=close_text,
            font=ctk.CTkFont(family="Arial", size=12, weight="bold"),
            width=200,
            height=36,
            corner_radius=18,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            text_color="#FFFFFF",
            command=self.show_main_menu
        )
        self.close_btn.place(relx=0.90, rely=0.90, anchor="center", relwidth=0.16)

    # ---------- Обновление UI и таймера ----------

    def update_ui(self) -> None:
        if not self.current_question_data:
            return

        # Update dynamic question counter indicator in the top-left
        if hasattr(self, "counter_btn"):
            self.counter_btn.configure(text=f"{self.engine.current_level + 1:02d}/15")

        self.question_label.configure(text=self.current_question_data["question"])

        options = self.current_question_data.get("options", [])
        for i, btn in enumerate(self.answer_buttons):
            if i < len(options):
                btn.configure(
                    text=f"{chr(ord('A') + i)}: {options[i]}",
                    fg_color="#411A60",
                    hover_color="#592584",
                    text_color="#E5C158",
                    border_color="#B59341",
                    state="normal",
                )
            else:
                btn.configure(text="", state="disabled")

        # Update lifeline buttons state
        self.btn_5050.configure(
            state="disabled" if self.engine.used_hints.get("50_50") else "normal",
            fg_color="#555555" if self.engine.used_hints.get("50_50") else "#721C24",
        )
        self.btn_audience.configure(
            state="disabled" if self.engine.used_hints.get("audience") else "normal",
            fg_color="#555555" if self.engine.used_hints.get("audience") else "#FFC107",
        )
        self.btn_call_friend.configure(
            state="disabled" if self.used_call_friend else "normal",
            fg_color="#555555" if self.used_call_friend else "#28C745",
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

        # Check settings for timer
        settings = self.data_manager.get_settings()
        timer_enabled = settings.get("timer_in_game", True)

        if timer_enabled:
            self.timer_label.place(relx=0.38, rely=0.58, anchor="center")
            self.time_left = 30
            self._update_timer_label()
            self._start_timer()
        else:
            self.timer_label.place_forget()
            self.time_left = 30 # Just in case logic expects a value

    def _update_timer_label(self) -> None:
        self.timer_label.configure(text=self.tr("in_game.timer", t=self.time_left))

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
        """Update money ladder UI with highlights for current level and achieved milestones."""
        level = self.engine.current_level
        max_levels = len(self.prize_levels)
        
        for i, (num_lbl, amount_lbl, row_frame) in enumerate(self.prize_labels):
            real_level_idx = max_levels - 1 - i  # 0 to 14
            level_num = real_level_idx + 1      # 1 to 15
            
            is_active = (real_level_idx == level)
            
            if is_active:
                # Active step: Bright green pill-box highlight
                color = "#FFFFFF"
                font_weight = "bold"
                font_size = 12
                bg_color = "#28C745"
            else:
                # Inactive step: Simple white text
                color = "#FFFFFF"
                font_weight = "normal"
                font_size = 12
                bg_color = "transparent"
            
            current_font = ctk.CTkFont(family=FONTS["ladder"], size=font_size, weight=font_weight)
            
            num_lbl.configure(text_color=color, font=current_font)
            amount_lbl.configure(text_color=color, font=current_font)
            row_frame.configure(fg_color=bg_color, corner_radius=10)

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
        """Finalize answer with proper error handling and state management."""
        try:
            correct_index = self.current_question_data.get("correct_index", -1)
            is_correct = index == correct_index

            # Получить уровень вопроса и время ответа
            level = self.engine.current_level + 1
            time_taken = 30 - self.time_left  # Calculate time taken for answer

            # Update win streak tracking
            if is_correct:
                self.current_streak += 1
                if self.current_streak > self.max_streak_in_game:
                    self.max_streak_in_game = self.current_streak
                print(f"DEBUG: Correct answer - Current streak: {self.current_streak}, Max streak: {self.max_streak_in_game}")
            else:
                self.current_streak = 0
                print(f"DEBUG: Wrong answer - Streak reset to 0, Max streak remains: {self.max_streak_in_game}")
            
            # Update stats using new global system
            self.data_manager.update_stats(is_correct)
            
            # Also update IQ and achievements with time tracking
            self.data_manager.update_correct_answers(is_correct, level, time_taken)
            
            # Achievement tracking
            self._track_achievements(is_correct, level, time_taken)

            if is_correct:
                self.sound_manager.play("correct_answer.mp3")
                self.engine.check_answer(index)
                btn.configure(fg_color="#2e7d32", text_color="white")

                def after_correct() -> None:
                    try:
                        next_question = self.engine.get_current_question()
                        if next_question is None:
                            self.show_game_over(win=True)
                        else:
                            self.load_next_question()
                    except Exception as e:
                        print(f"Error in after_correct: {e}")
                        self.show_game_over(win=False)

                self.after(1500, after_correct)
                return

            # Handle incorrect answers
            self.sound_manager.stop_bg_music()
            self.sound_manager.play("wrong_answer.mp3")
            btn.configure(fg_color="#b71c1c", text_color="white")

            # Check if safety net is active
            if self.safety_net_active:
                self.safety_net_active = False

                def restore() -> None:
                    try:
                        for b in self.answer_buttons:
                            if not b.cget("text"):
                                b.configure(state="disabled")
                                continue
                            b.configure(
                                fg_color="#411A60",
                                hover_color="#592584",
                                text_color="#E5C158",
                                border_color="#B59341",
                                state="normal",
                            )
                        self.time_left = 30
                        self._update_timer_label()
                        self._start_timer()

                        dialog = ctk.CTkToplevel(self)
                        dialog.title(self.tr("dialogs.right_to_mistake.title"))
                        dialog.geometry("360x160")
                        label = ctk.CTkLabel(
                            dialog,
                            text=self.tr("dialogs.right_to_mistake.body"),
                            wraplength=320,
                        )
                        label.pack(padx=20, pady=20)
                        ctk.CTkButton(dialog, text=self.tr("dialogs.ok"), command=dialog.destroy).pack(pady=(0, 15))
                    except Exception as e:
                        print(f"Error in safety net restore: {e}")
                    finally:
                        self.is_processing = False

                self.after(800, restore)
            else:
                # No safety net - game over
                self.after(1500, lambda: self.show_game_over(win=False))

        except Exception as e:
            print(f"Critical error in finalize_answer: {e}")
            # Emergency fallback to prevent freezing
            self.is_processing = False
            self.show_game_over(win=False)

    def _track_achievements(self, is_correct: bool, level: int, time_taken: int) -> None:
        """Track and unlock achievements based on game events."""
        session_stats = self.data_manager.get_session_stats()
        
        # Update session stats
        if is_correct:
            session_stats["current_session_correct"] += 1
            # Track fast answers for cold_blood achievement
            if time_taken <= 10:
                session_stats["fast_answers_count"] += 1
        
        # Track hints used for current question
        session_stats["current_question_hints"].append({
            "level": level,
            "hints_used": []
        })
        
        self.data_manager.update_session_stats(**session_stats)
        
        # Check for rank up based on current level
        self.data_manager.check_rank_up(current_level=level)
        
        # Check achievements
        
        # First step - first correct answer
        if is_correct and not self.data_manager.is_achievement_unlocked("first_step"):
            self.data_manager.unlock_achievement("first_step")
        
        # Cold blood - 10 fast answers
        if session_stats["fast_answers_count"] >= 10 and not self.data_manager.is_achievement_unlocked("cold_blood"):
            self.data_manager.unlock_achievement("cold_blood")
        
        # On the edge - correct answer with less than 2 seconds left
        if is_correct and self.time_left <= 2 and not self.data_manager.is_achievement_unlocked("on_the_edge"):
            self.data_manager.unlock_achievement("on_the_edge")
        
        # Jackpot - reach final question (15)
        if level == 15 and is_correct and not self.data_manager.is_achievement_unlocked("jackpot"):
            self.data_manager.unlock_achievement("jackpot")
        
        # Veteran - 500 total correct answers
        stats = self.data_manager.get_statistics()
        if stats["total_correct_answers"] >= 500 and not self.data_manager.is_achievement_unlocked("veteran"):
            self.data_manager.unlock_achievement("veteran")
        
        # History expert - track category answers (using level 1 as proxy for history)
        if is_correct and level == 1:
            category_answers = session_stats.get("category_answers", {})
            category_answers["history"] = category_answers.get("history", 0) + 1
            session_stats["category_answers"] = category_answers
            if category_answers["history"] >= 50 and not self.data_manager.is_achievement_unlocked("history_expert"):
                self.data_manager.unlock_achievement("history_expert")

    def _check_game_end_achievements(self, win: bool, win_amount: int) -> None:
        """Check achievements at game end."""
        session_stats = self.data_manager.get_session_stats()
        current_level = self.engine.current_level + 1
        
        # First million - win 1,000,000 in one game
        if win and win_amount >= 1000000 and not self.data_manager.is_achievement_unlocked("first_million"):
            self.data_manager.unlock_achievement("first_million")
        
        # Own mind - complete game without any hints
        if win and not any(session_stats["current_session_hints"].values()) and not self.data_manager.is_achievement_unlocked("own_mind"):
            self.data_manager.unlock_achievement("own_mind")
        
        # Bitter experience - lose on final 15th question
        if not win and current_level == 15 and not self.data_manager.is_achievement_unlocked("bitter_experience"):
            self.data_manager.unlock_achievement("bitter_experience")
        
        # Sprinter - complete game in under 2 minutes
        import time
        game_duration = time.time() - session_stats.get("game_start_time", time.time())
        if win and game_duration <= 120 and not self.data_manager.is_achievement_unlocked("sprinter"):
            self.data_manager.unlock_achievement("sprinter")
        
        # Update total capital for magnate achievement
        total_capital = session_stats.get("total_capital", 0) + win_amount
        if total_capital >= 1000000000 and not self.data_manager.is_achievement_unlocked("magnate"):
            self.data_manager.unlock_achievement("magnate")
        
        # Update consecutive games tracking
        if win or (current_level >= 5 and not win):  # Win or reach safety net
            consecutive_games = session_stats.get("consecutive_games", 0) + 1
            if consecutive_games >= 3 and not self.data_manager.is_achievement_unlocked("intellectual_series"):
                self.data_manager.unlock_achievement("intellectual_series")
        else:
            consecutive_games = 0  # Reset consecutive games
        
        # Check for club legend achievement
        achievements_data = self.data_manager.get_achievements_data()
        unlocked_count = sum(1 for achievement in achievements_data["achievements"].values() 
                           if achievement["is_unlocked"] and achievement["id"] != "club_legend")
        if unlocked_count >= 19 and not self.data_manager.is_achievement_unlocked("club_legend"):
            self.data_manager.unlock_achievement("club_legend")
        
        # Check for rank up
        self.data_manager.check_rank_up(current_level=current_level, game_completed=win)

        # Reset session stats for next game
        self.data_manager.update_session_stats(
            current_session_correct=0,
            current_session_hints={"50_50": False, "audience": False, "call_friend": False},
            current_question_hints=[],
            fast_answers_count=0,
            game_start_time=time.time(),
            consecutive_games=consecutive_games,
            total_capital=total_capital
        )

    def _save_score_on_loss(self) -> None:
        """Save the current safe score to database when player gives wrong answer."""
        try:
            # Calculate REAL game duration using self.start_time
            import time
            if hasattr(self, 'start_time') and self.start_time:
                game_time_seconds = int(time.time() - self.start_time)
                print(f"LOSS SAVE: Real game duration: {game_time_seconds} seconds")
            else:
                # Fallback to session stats
                session_stats = self.data_manager.get_session_stats()
                game_start_time = session_stats.get("game_start_time", time.time())
                game_time_seconds = int(time.time() - game_start_time)
                print(f"LOSS SAVE: Fallback game duration: {game_time_seconds} seconds")
            
            # Determine safe amount based on current level
            current_level = self.engine.current_level
            if current_level >= 5:  # Safety net at level 5 (question 6)
                safe_amount = int(self.prize_levels[4].replace(" ", "").replace("₽", ""))  # Level 5 amount
            else:
                safe_amount = 0
            
            print(f"LOSS SAVE: Safe amount for level {current_level}: {safe_amount} ₽")
            
            # Get player name with fallback
            profile = self.data_manager.get_profile()
            player_name = profile.get("name", "RUS").strip()
            if player_name == "Anonymous":
                player_name = "RUS"
            
            # Save to database immediately
            if player_name:
                print(f"LOSS SAVE: Triggering database save for {player_name}")
                print(f"LOSS SAVE: Data - Score: {safe_amount}, Time: {game_time_seconds}s, Max Streak: {self.max_streak_in_game}")
                
                success = self.db_manager.add_score(
                    name=player_name,
                    score=safe_amount,
                    time_seconds=game_time_seconds,
                    series=str(self.max_streak_in_game)
                )
                
                if success:
                    print(f"LOSS SAVE: Database save successful for {player_name}")
                else:
                    print(f"LOSS SAVE: Database save failed for {player_name}")
            else:
                print("LOSS SAVE: No valid player name - not saving to database")
                
        except Exception as e:
            print(f"LOSS SAVE: Error saving score on loss: {e}")
            import traceback
            traceback.print_exc()

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
            
            # Track hint usage for achievements
            self._track_hint_usage("50_50")
        except Exception as e:
            print(f"Ошибка подсказки 50/50: {e}")

    def _track_hint_usage(self, hint_type: str) -> None:
        """Track hint usage for achievements."""
        session_stats = self.data_manager.get_session_stats()
        current_level = self.engine.current_level + 1
        
        # Update session stats
        session_stats["current_session_hints"][hint_type] = True
        
        # Add hint to current question tracking
        if session_stats["current_question_hints"]:
            session_stats["current_question_hints"][-1]["hints_used"].append(hint_type)
        
        self.data_manager.update_session_stats(**session_stats)
        
        # Check achievements
        
        # Risky guy - reach level 10 without hints
        if current_level >= 10 and not any(session_stats["current_session_hints"].values()) and not self.data_manager.is_achievement_unlocked("risky_guy"):
            self.data_manager.unlock_achievement("risky_guy")
        
        # Va-bank - use all three hints on one question
        current_hints = session_stats["current_question_hints"][-1]["hints_used"] if session_stats["current_question_hints"] else []
        if len(set(current_hints)) >= 3 and not self.data_manager.is_achievement_unlocked("va_bank"):
            self.data_manager.unlock_achievement("va_bank")

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
            
            # Track hint usage for achievements
            self._track_hint_usage("audience")
            
            # Check voice_of_people achievement - win with audience help
            correct_index = self.current_question_data.get("correct_index", -1)
            audience_choice = max(stats.items(), key=lambda x: x[1])[0]
            if audience_choice == correct_index and not self.data_manager.is_achievement_unlocked("voice_of_people"):
                # This will be checked in finalize_answer when they answer correctly
                pass

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
        
        # Track hint usage for achievements
        self._track_hint_usage("call_friend")
        
        # Check friend_in_need achievement - use call friend above level 10 and answer correctly
        current_level = self.engine.current_level + 1
        if current_level > 10 and idx == self.current_question_data.get("correct_index", -1) and not self.data_manager.is_achievement_unlocked("friend_in_need"):
            self.data_manager.unlock_achievement("friend_in_need")

    def _on_second_chance(self) -> None:
        if self.safety_net_active or self.is_processing:
            return
        self.safety_net_active = True
        self.btn_second_chance.configure(
            fg_color="#15803d", hover_color="#16a34a", text_color="#ffffff"
        )

    def _take_money(self) -> None:
        """Handle take money functionality."""
        if self.is_processing or not self.current_question_data:
            return
        
        current_level = self.engine.current_level + 1
        if current_level < 1:
            return
        
        # Calculate winnings: "take money" is the last COMPLETED level.
        # engine.current_level is the index of the current question (0-based).
        completed_level_idx = self.engine.current_level - 1
        if 0 <= completed_level_idx < len(self.prize_levels):
            winnings = int(self.prize_levels[completed_level_idx].replace(" ", "").replace("₽", ""))
        else:
            winnings = 0
        
        # Track take money usage for achievements
        session_stats = self.data_manager.get_session_stats()
        take_money_count = session_stats.get("take_money_count", 0) + 1
        
        # Check bird in hand achievement - take money above level 12
        if current_level > 12 and not self.data_manager.is_achievement_unlocked("bird_in_hand"):
            self.data_manager.unlock_achievement("bird_in_hand")
        
        # Check cautious strategist achievement - take money 20 times
        if take_money_count >= 20 and not self.data_manager.is_achievement_unlocked("cautious_strategist"):
            self.data_manager.unlock_achievement("cautious_strategist")
        
        # Update session stats
        self.data_manager.update_session_stats(take_money_count=take_money_count)
        
        # Stop timer
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None
        
        # Show take money dialog and end game
        self.show_game_over(win=False, take_money_amount=winnings)

    # ---------- Окно профиля ----------

    def show_profile_window(self) -> None:
        self.switch_frame(ProfileFrame)

    # ---------- Окно настроек ----------

    def show_settings_window(self) -> None:
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

    def show_game_over(self, win: bool, take_money_amount: int = 0) -> None:
        """Show game over screen with proper error handling and async safety."""
        # Strict one-shot lock to prevent infinite loops / repeated windows
        if getattr(self, "_game_ending_processed", False):
            return
        self._game_ending_processed = True
        # Keep legacy flags in sync (used elsewhere)
        self._already_ended = True
        self._is_game_over_processed = True
        
        # Stop all timers and music immediately
        try:
            if self._timer_id is not None:
                self.after_cancel(self._timer_id)
                self._timer_id = None
            self.sound_manager.stop_bg_music()
        except Exception:
            pass
        
        try:
            # ---- Clean flow: Lock -> Capture Prize -> Save -> Show UI ----
            # Determine final prize FIRST (must not depend on any later resets/cleanup).
            final_prize = 0
            if take_money_amount > 0:
                final_prize = int(take_money_amount)
            elif win:
                # When the last question is answered, engine.current_level can be 15 (past the ladder).
                idx = min(max(self.engine.current_level, 0), len(self.prize_levels) - 1)
                final_prize = int(self.prize_levels[idx].replace(" ", "").replace("₽", ""))
            else:
                # Loss: use last "safe" milestone (currently level 5).
                current_level_idx = getattr(self.engine, "current_level", 0)
                if current_level_idx >= 5:
                    final_prize = int(self.prize_levels[4].replace(" ", "").replace("₽", ""))
                else:
                    final_prize = 0

            # Save to DB immediately (before any UI teardown that might trigger side-effects).
            try:
                import time
                if hasattr(self, "start_time") and self.start_time:
                    game_time_seconds = int(time.time() - self.start_time)
                else:
                    session_stats = self.data_manager.get_session_stats()
                    game_start_time = session_stats.get("game_start_time", time.time())
                    game_time_seconds = int(time.time() - game_start_time)

                profile = self.data_manager.get_profile() or {}
                player_name = (profile.get("name") or "").strip() or getattr(self, "current_player_name", "") or "RUS"
                if player_name == "Anonymous":
                    player_name = "RUS"

                print(f"FINAL DEBUG: Saving {player_name} with {final_prize} to DB")
                self.db_manager.add_score(
                    name=player_name,
                    score=int(final_prize),
                    time_seconds=int(game_time_seconds),
                    series=str(getattr(self, "max_streak_in_game", 0)),
                )
            except Exception as e:
                print(f"GAME END: Error saving game result (early): {e}")

            # Destroy game frames safely
            frames_to_destroy = [
                ("lifeline_frame", self.lifeline_frame),
                ("main_frame", self.main_frame),
                ("sidebar_frame", self.sidebar_frame)
            ]
            
            for frame_name, frame_obj in frames_to_destroy:
                if frame_obj is not None:
                    try:
                        frame_obj.destroy()
                        setattr(self, frame_name, None)
                    except Exception as e:
                        print(f"Error destroying {frame_name}: {e}")

            # Destroy game background label to wipe out all direct child widgets automatically
            if getattr(self, "game_bg_label", None) is not None:
                try:
                    self.game_bg_label.destroy()
                except Exception:
                    pass
                self.game_bg_label = None

            # Create end frame
            end_frame = ctk.CTkFrame(self, fg_color="transparent")
            end_frame.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=20, pady=20)
            self.current_frame = end_frame
            
            end_frame.grid_columnconfigure(0, weight=1)
            end_frame.grid_rowconfigure(0, weight=1)
            end_frame.grid_rowconfigure(1, weight=0)
            end_frame.grid_rowconfigure(2, weight=0)
            end_frame.grid_rowconfigure(3, weight=0)
            
            # Stop background music safely
            try:
                self.sound_manager.stop_bg_music()
            except Exception as e:
                print(f"Error stopping background music: {e}")
            
            # Determine game outcome
            if take_money_amount > 0:
                title_text = self.tr("gameover.take_money")
                color = "#ffd700"
                win_amount = final_prize
            elif win:
                title_text = self.tr("gameover.win_millionaire")
                color = "#00ff00"
                win_amount = final_prize
            else:
                title_text = self.tr("gameover.end")
                color = "#ff0000"
                win_amount = final_prize

            # Update profile with error handling
            try:
                self.data_manager.update_profile(win_amount)
            except Exception as e:
                print(f"Error updating profile: {e}")
            
            # Check achievements with error handling
            try:
                self._check_game_end_achievements(win, win_amount)
            except Exception as e:
                print(f"Error checking game end achievements: {e}")

            # (DB save already done above; keep UI work below deterministic.)

            # Create title label
            title_lbl = ctk.CTkLabel(
                end_frame,
                text=title_text,
                font=ctk.CTkFont(size=40, weight="bold"),
                text_color=color,
            )
            title_lbl.grid(row=0, column=0, pady=20)

            # Create restart button
            restart_btn = ctk.CTkButton(
                end_frame,
                text=self.tr("gameover.restart"),
                font=ctk.CTkFont(size=20),
                command=lambda: self.restart_game(end_frame),
            )
            restart_btn.grid(row=2, column=0, pady=10)

            # Create return to menu button
            return_btn = ctk.CTkButton(
                end_frame,
                text=self.tr("gameover.return_to_menu"),
                font=ctk.CTkFont(size=20),
                command=self.show_main_menu,
            )
            return_btn.grid(row=3, column=0, pady=10)

        except Exception as e:
            print(f"Critical error in show_game_over: {e}")
            # Emergency fallback - show minimal game over screen
            try:
                for widget in self.winfo_children():
                    widget.destroy()
                
                emergency_frame = ctk.CTkFrame(self, fg_color="#020b23")
                emergency_frame.pack(fill="both", expand=True)
                
                ctk.CTkLabel(
                    emergency_frame,
                        text=self.tr("gameover.end"),
                    font=ctk.CTkFont(size=24, weight="bold"),
                    text_color="#ff0000"
                ).pack(expand=True)
                
                ctk.CTkButton(
                    emergency_frame,
                        text=self.tr("menu.main_menu"),
                    command=self.show_main_menu
                ).pack(pady=20)
            except Exception as emergency_e:
                print(f"Emergency fallback failed: {emergency_e}")
                self.destroy()  # Last resort

    def restart_game(self, end_frame: ctk.CTkFrame) -> None:
        """Restarts the game immediately from the game over screen."""
        self.start_game()

    
    def _add_record(self) -> None:
        """Save game record to SQLite database with proper error handling."""
        try:
            import time
            
            # Calculate game time safely
            session_stats = self.data_manager.get_session_stats()
            game_start_time = session_stats.get("game_start_time", time.time())
            game_time_seconds = int(time.time() - game_start_time)
            
            # Get current rank safely
            current_rank = self.data_manager.get_current_rank()
            
            profile = self.data_manager.get_profile()
            if profile and profile.get("name"):
                try:
                    score_str = self.prize_levels[self.engine.current_level]
                    score = int(score_str.replace(" ", "").replace("₽", ""))
                    
                    # Save to SQLite database with timeout to prevent freezing
                    success = self.db_manager.add_score(
                        name=profile["name"],
                        score=score,
                        time_seconds=game_time_seconds,
                        series=str(current_rank)
                    )
                    
                    if success:
                        print(f"Record saved to database: {profile['name']} - {score} ₽ - {game_time_seconds}s - {current_rank}")
                    else:
                        print(f"Failed to save record to database")
                        
                except (ValueError, IndexError) as e:
                    print(f"Error parsing score: {e}")
                except Exception as e:
                    print(f"Error saving record to database: {e}")
                    
            else:
                # If no profile, ask for name with proper cleanup
                try:
                    dialog = ctk.CTkToplevel(self)
                    dialog.title("Новый рекорд!")
                    dialog.geometry("300x200")
                    dialog.attributes("-topmost", True)

                    label = ctk.CTkLabel(dialog, text="Введите ваше имя:")
                    label.pack(pady=20)

                    name_entry = ctk.CTkEntry(dialog, placeholder_text="Имя")
                    name_entry.pack(pady=10)

                    def save_record():
                        try:
                            name = name_entry.get().strip()
                            if name:
                                score_str = self.prize_levels[self.engine.current_level]
                                score = int(score_str.replace(" ", "").replace("₽", ""))
                                
                                # Save to SQLite database
                                success = self.db_manager.add_score(
                                    name=name,
                                    score=score,
                                    time_seconds=game_time_seconds,
                                    series=str(current_rank)
                                )
                                
                                if success:
                                    print(f"Record saved to database: {name} - {score} ₽ - {game_time_seconds}s - {current_rank}")
                                else:
                                    print(f"Failed to save record to database")
                                    
                        except (ValueError, IndexError) as e:
                            print(f"Error parsing score in dialog: {e}")
                        except Exception as e:
                            print(f"Error saving record in dialog: {e}")
                        finally:
                            dialog.destroy()

                    save_btn = ctk.CTkButton(dialog, text="Сохранить", command=save_record)
                    save_btn.pack(pady=10)
                    
                except Exception as e:
                    print(f"Error creating name dialog: {e}")
                    
        except Exception as e:
            print(f"Critical error in _add_record: {e}")
