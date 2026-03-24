import customtkinter as ctk
import secrets
import string
import pyperclip
import hashlib
import json
import os
import webbrowser
import threading
from datetime import datetime

APP_DIR = os.path.join(os.path.expanduser("~"), ".passworlds")
os.makedirs(APP_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APP_DIR, "settings.json")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
MASTER_FILE = os.path.join(APP_DIR, "master.json")
VERSION = "1.0.2"

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(f"PassWorlds {VERSION}")
        self.geometry("550x750")
        self.resizable(False, False)
        
        self.password = ""
        self.password_history = []
        self.hibp_count = 0
        self.is_locked = False
        self.master_password_hash = ""
        self.last_activity = datetime.now()
        self.load_master_password()
        
        self.load_settings()
        self.load_history()
        
        color_eng_to_rus = {
            "blue": "Синий",
            "cyan": "Голубой",
            "red": "Красный",
            "pink": "Розовый",
            "green": "Зелёный",
            "lime": "Салатовый",
            "purple": "Фиолетовый"
        }
        
        ctk.set_appearance_mode(self.settings["theme"])
        
        eng_color = color_eng_to_rus.get(self.settings["color_theme"], self.settings["color_theme"])
        if eng_color in ["blue", "green", "dark-blue"]:
            ctk.set_default_color_theme(eng_color)
        
        self.setup_ui()
        self.apply_color_theme(self.settings["color_theme"])
        self.bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        if self.has_master_password():
            self.withdraw()
            self.show_startup_auth()
    
    def show_startup_auth(self):
        login_win = ctk.CTkToplevel(self)
        login_win.title("Вход")
        login_win.geometry("350x200")
        login_win.resizable(False, False)
        login_win.transient(self)
        
        ctk.CTkLabel(login_win, text="Введите мастер-пароль:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        
        password_entry = ctk.CTkEntry(login_win, show="*", width=250, font=ctk.CTkFont(size=14))
        password_entry.pack(pady=10)
        
        def try_login():
            if self.verify_master_password(password_entry.get()):
                self.is_locked = False
                self.last_activity = datetime.now()
                login_win.destroy()
                self.deiconify()
            else:
                ctk.CTkMessagebox(title="Ошибка", message="Неверный пароль!", icon="cancel")
        
        def exit_app():
            login_win.destroy()
            self.destroy()
        
        ctk.CTkButton(login_win, text="Войти", command=try_login, width=100).pack(pady=10)
        ctk.CTkButton(login_win, text="Выход", command=exit_app, fg_color="red", hover_color="darkred", width=100).pack(pady=5)
        
        password_entry.focus()
        login_win.bind("<Return>", lambda e: try_login())
    
    def load_settings(self):
        color_eng_to_rus = {
            "blue": "Синий",
            "cyan": "Голубой",
            "red": "Красный",
            "pink": "Розовый",
            "green": "Зелёный",
            "lime": "Салатовый",
            "purple": "Фиолетовый"
        }
        default_settings = {
            "theme": "light",
            "color_theme": "Синий",
            "default_length": 16,
            "use_upper": True,
            "use_lower": True,
            "use_digits": True,
            "use_special": True,
            "auto_check_hibp": True,
            "auto_lock_timeout": 5
        }
        
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                loaded = json.load(f)
                if loaded.get("color_theme") in color_eng_to_rus:
                    loaded["color_theme"] = color_eng_to_rus[loaded["color_theme"]]
                self.settings = {**default_settings, **loaded}
        else:
            self.settings = default_settings
    
    def save_settings(self):
        color_rus_to_eng = {
            "Синий": "blue",
            "Голубой": "cyan",
            "Красный": "red",
            "Розовый": "pink",
            "Зелёный": "green",
            "Салатовый": "lime",
            "Фиолетовый": "purple"
        }
        settings_to_save = self.settings.copy()
        if settings_to_save.get("color_theme") in color_rus_to_eng:
            settings_to_save["color_theme"] = color_rus_to_eng[settings_to_save["color_theme"]]
        with open(CONFIG_FILE, "w") as f:
            json.dump(settings_to_save, f, indent=2)
    
    def load_master_password(self):
        if os.path.exists(MASTER_FILE):
            with open(MASTER_FILE, "r") as f:
                data = json.load(f)
                self.master_password_hash = data.get("hash", "")
        else:
            self.master_password_hash = ""
    
    def save_master_password(self, password):
        if password:
            hash_obj = hashlib.sha256(password.encode())
            self.master_password_hash = hash_obj.hexdigest()
            with open(MASTER_FILE, "w") as f:
                json.dump({"hash": self.master_password_hash}, f)
        else:
            self.master_password_hash = ""
            if os.path.exists(MASTER_FILE):
                os.remove(MASTER_FILE)
    
    def verify_master_password(self, password):
        if not self.master_password_hash:
            return True
        hash_obj = hashlib.sha256(password.encode())
        return hash_obj.hexdigest() == self.master_password_hash
    
    def has_master_password(self):
        return bool(self.master_password_hash)
    
    def check_auto_lock(self):
        if not self.has_master_password() or self.is_locked:
            return
        timeout = self.settings.get("auto_lock_timeout", 5)
        if timeout > 0:
            elapsed = (datetime.now() - self.last_activity).total_seconds()
            if elapsed > timeout * 60:
                self.lock_app()
    
    def lock_app(self):
        self.is_locked = True
        self.withdraw()
        self.show_login_screen()
    
    def show_login_screen(self):
        login_win = ctk.CTkToplevel(self)
        login_win.title("Вход")
        login_win.geometry("350x200")
        login_win.resizable(False, False)
        login_win.transient(self)
        
        ctk.CTkLabel(login_win, text="Введите мастер-пароль:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=20)
        
        password_entry = ctk.CTkEntry(login_win, show="*", width=250, font=ctk.CTkFont(size=14))
        password_entry.pack(pady=10)
        
        def try_login():
            if self.verify_master_password(password_entry.get()):
                self.is_locked = False
                self.last_activity = datetime.now()
                login_win.destroy()
                self.deiconify()
            else:
                ctk.CTkMessagebox(title="Ошибка", message="Неверный пароль!", icon="cancel")
        
        def cancel_login():
            login_win.destroy()
            if self.is_locked:
                self.destroy()
        
        ctk.CTkButton(login_win, text="Войти", command=try_login, width=100).pack(pady=10)
        ctk.CTkButton(login_win, text="Выход", command=cancel_login, fg_color="red", hover_color="darkred", width=100).pack(pady=5)
        
        password_entry.focus()
        login_win.bind("<Return>", lambda e: try_login())
    
    def reset_activity(self, event=None):
        self.last_activity = datetime.now()
    
    def apply_color_theme(self, color_name):
        color_map = {
            "Синий": ("#3b8ed0", "#1f6aa5"),
            "Голубой": ("#00a8cc", "#007a99"),
            "Красный": ("#e74c3c", "#c0392b"),
            "Розовый": ("#e91e8a", "#c01774"),
            "Зелёный": ("#27ae60", "#1e8449"),
            "Салатовый": ("#8bc34a", "#689f38"),
            "Фиолетовый": ("#9b59b6", "#8e44ad"),
            "blue": ("#3b8ed0", "#1f6aa5"),
            "green": ("#27ae60", "#1e8449"),
            "dark-blue": ("#3b8ed0", "#1f6aa5")
        }
        colors = color_map.get(color_name, color_map["Синий"])
        
        buttons_to_update = [self.settings_btn, self.history_btn, self.generate_btn, self.copy_btn]
        if hasattr(self, 'reset_btn'):
            buttons_to_update.append(self.reset_btn)
        
        for btn in buttons_to_update:
            btn.configure(fg_color=colors[0], hover_color=colors[1])
        
        self.length_slider.configure(button_color=colors[0], button_hover_color=colors[1])
        
        for cb in [self.uppercase_cb, self.lowercase_cb, self.digits_cb, self.special_cb, self.custom_password_cb]:
            cb.configure(fg_color=colors[0], hover_color=colors[1])
    
    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r") as f:
                    self.password_history = json.load(f)
            except:
                self.password_history = []
    
    def save_history(self):
        with open(HISTORY_FILE, "w") as f:
            json.dump(self.password_history[-100:], f, indent=2)
    
    def setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(pady=15)
        
        try:
            from PIL import Image
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "passworlds_icon.png")
            if os.path.exists(icon_path):
                icon_img = ctk.CTkImage(Image.open(icon_path), size=(60, 60))
                icon_label = ctk.CTkLabel(header_frame, image=icon_img, text="")
                icon_label.pack(side="left", padx=(0, 10))
        except:
            pass
        
        self.title_label = ctk.CTkLabel(
            header_frame, 
            text="Генератор паролей",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(side="left")
        
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=5, padx=20, fill="x")
        
        self.settings_btn = ctk.CTkButton(
            top_frame,
            text="Настройки",
            width=90,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.open_settings_window
        )
        self.settings_btn.pack(side="left", padx=2)
        
        self.history_btn = ctk.CTkButton(
            top_frame,
            text="История",
            width=80,
            height=30,
            font=ctk.CTkFont(size=12),
            command=self.open_history_window
        )
        self.history_btn.pack(side="left", padx=2)
        
        self.password_frame = ctk.CTkFrame(self)
        self.password_frame.pack(pady=10, padx=20, fill="x")
        
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            font=ctk.CTkFont(size=18),
            height=50,
            placeholder_text="Нажмите 'Сгенерировать' или Ctrl+G",
            state="readonly"
        )
        self.password_entry.pack(pady=10, padx=10, fill="x")
        
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill="x")
        
        self.generate_btn = ctk.CTkButton(
            self.button_frame,
            text="Сгенерировать (Ctrl+G)",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            command=self.generate_password
        )
        self.generate_btn.pack(pady=5, fill="x")
        
        self.copy_btn = ctk.CTkButton(
            self.button_frame,
            text="Копировать",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.copy_password,
            state="disabled"
        )
        self.copy_btn.pack(pady=5, fill="x")
        
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=10, padx=20, fill="x")
        
        self.length_label = ctk.CTkLabel(
            self.settings_frame, 
            text=f"Длина пароля: {self.settings['default_length']}", 
            font=ctk.CTkFont(size=14)
        )
        self.length_label.pack(pady=(15, 5))
        
        self.length_slider = ctk.CTkSlider(
            self.settings_frame,
            from_=4,
            to=64,
            number_of_steps=60,
            command=self.update_length_label
        )
        self.length_slider.set(self.settings["default_length"])
        self.length_slider.pack(pady=5, padx=20, fill="x")
        
        self.checkbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.checkbox_frame.pack(pady=10, padx=20)
        
        self.uppercase_var = ctk.BooleanVar(value=self.settings["use_upper"])
        self.uppercase_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="A-Z Заглавные",
            variable=self.uppercase_var,
            font=ctk.CTkFont(size=14)
        )
        self.uppercase_cb.pack(pady=3, anchor="w")
        
        self.lowercase_var = ctk.BooleanVar(value=self.settings["use_lower"])
        self.lowercase_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="a-z Строчные",
            variable=self.lowercase_var,
            font=ctk.CTkFont(size=14)
        )
        self.lowercase_cb.pack(pady=3, anchor="w")
        
        self.digits_var = ctk.BooleanVar(value=self.settings["use_digits"])
        self.digits_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="0-9 Цифры",
            variable=self.digits_var,
            font=ctk.CTkFont(size=14)
        )
        self.digits_cb.pack(pady=3, anchor="w")
        
        self.special_var = ctk.BooleanVar(value=self.settings["use_special"])
        self.special_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="!@#$%^&* Спецсимволы",
            variable=self.special_var,
            font=ctk.CTkFont(size=14)
        )
        self.special_cb.pack(pady=3, anchor="w")
        
        self.custom_password_var = ctk.BooleanVar(value=False)
        self.custom_password_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="✎ Придумать свой пароль",
            variable=self.custom_password_var,
            font=ctk.CTkFont(size=14),
            command=self.toggle_custom_password
        )
        self.custom_password_cb.pack(pady=3, anchor="w")
        
        self.info_frame = ctk.CTkFrame(self)
        self.info_frame.pack(pady=10, padx=20, fill="x")
        
        self.strength_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.strength_label.pack(pady=5)
        
        self.hibp_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12),
            cursor="hand2"
        )
        self.hibp_label.pack(pady=2)
        self.hibp_label.bind("<Button-1>", lambda e: self.open_hibp_info())
        
        self.entropy_label = ctk.CTkLabel(
            self.info_frame,
            text="",
            font=ctk.CTkFont(size=12)
        )
        self.entropy_label.pack(pady=2)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            text_color="green",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
        
        self.bind("<Motion>", self.reset_activity)
        self.bind("<Key>", self.reset_activity)
        self.bind("<Button>", self.reset_activity)
        
        self.check_lock_timer()
    
    def check_lock_timer(self):
        self.check_auto_lock()
        self.after(10000, self.check_lock_timer)
    
    def bind_shortcuts(self):
        try:
            import keyboard
            self._keyboard_shortcuts = [
                keyboard.add_hotkey("ctrl+g", self.generate_password, suppress=True),
                keyboard.add_hotkey("ctrl+h", self.open_history_window, suppress=True)
            ]
            self.bind("<Control-g>", lambda e: None)
            self.bind("<Control-h>", lambda e: None)
        except:
            self.bind("<Control-g>", lambda e: self.generate_password())
            self.bind("<Control-h>", lambda e: self.open_history_window())
    
    def on_closing(self):
        try:
            import keyboard
            keyboard.unhook_all()
        except:
            pass
        self.destroy()
    
    def update_length_label(self, value):
        self.length_label.configure(text=f"Длина пароля: {int(value)}")
    
    def toggle_custom_password(self):
        if self.custom_password_var.get():
            self.length_slider.configure(state="disabled")
            self.uppercase_cb.configure(state="disabled")
            self.lowercase_cb.configure(state="disabled")
            self.digits_cb.configure(state="disabled")
            self.special_cb.configure(state="disabled")
            self.generate_btn.configure(state="disabled")
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.configure(placeholder_text="Введите свой пароль")
            self.password_entry.unbind("<KeyRelease>" if hasattr(self, '_key_bind_id') else "")
            self._key_bind_id = self.password_entry.bind("<KeyRelease>", lambda e: self.check_custom_password_strength())
            self.copy_btn.configure(state="normal")
        else:
            self.length_slider.configure(state="normal")
            self.uppercase_cb.configure(state="normal")
            self.lowercase_cb.configure(state="normal")
            self.digits_cb.configure(state="normal")
            self.special_cb.configure(state="normal")
            self.generate_btn.configure(state="normal")
            self.password = ""
            self.password_entry.configure(state="normal")
            self.password_entry.delete(0, "end")
            self.password_entry.configure(state="readonly", placeholder_text="Нажмите 'Сгенерировать' или Ctrl+G")
            self.strength_label.configure(text="")
            self.hibp_label.configure(text="")
            self.entropy_label.configure(text="")
            self.copy_btn.configure(state="normal")
    
    def check_custom_password_strength(self):
        password = self.password_entry.get()
        if not password:
            self.strength_label.configure(text="")
            self.hibp_label.configure(text="")
            self.entropy_label.configure(text="")
            return
        
        self.password = password
        
        strength = self.check_strength(password)
        self.strength_label.configure(text=f"Надёжность: {strength}")
        
        if strength == "Слабый":
            self.strength_label.configure(text_color="red")
        elif strength == "Средний":
            self.strength_label.configure(text_color="orange")
        else:
            self.strength_label.configure(text_color="green")
        
        length = len(password)
        chars = 0
        if any(c in string.ascii_uppercase for c in password):
            chars += 26
        if any(c in string.ascii_lowercase for c in password):
            chars += 26
        if any(c in string.digits for c in password):
            chars += 10
        if any(c in string.punctuation for c in password):
            chars += 32
        
        if chars > 0:
            import math
            entropy = length * math.log2(chars)
            self.entropy_label.configure(text=f"Энтропия: {entropy:.1f} бит")
        
        if self.settings.get("auto_check_hibp", True):
            self.check_hibp()
    
    def generate_password(self):
        length = int(self.length_slider.get())
        
        chars = ""
        if self.uppercase_var.get():
            chars += string.ascii_uppercase
        if self.lowercase_var.get():
            chars += string.ascii_lowercase
        if self.digits_var.get():
            chars += string.digits
        if self.special_var.get():
            chars += string.punctuation
        
        if not chars:
            chars = string.ascii_letters + string.digits
        
        self.password = ''.join(secrets.choice(chars) for _ in range(length))
        
        self.password_entry.configure(state="normal")
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, self.password)
        self.password_entry.configure(state="readonly")
        
        self.copy_btn.configure(state="normal")
        
        strength = self.check_strength(self.password)
        self.strength_label.configure(text=f"Надёжность: {strength}")
        
        if strength == "Слабый":
            self.strength_label.configure(text_color="red")
        elif strength == "Средний":
            self.strength_label.configure(text_color="orange")
        else:
            self.strength_label.configure(text_color="green")
        
        entropy = self.calculate_entropy(length, chars)
        self.entropy_label.configure(text=f"Энтропия: {entropy:.1f} бит")
        
        if self.settings.get("auto_check_hibp", True):
            self.check_hibp()
    
    def calculate_entropy(self, length, chars):
        if chars:
            return length * (len(chars) ** 0.5)
        return 0
    
    def check_strength(self, password):
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if len(password) >= 16:
            score += 1
        if any(c in string.ascii_lowercase for c in password):
            score += 1
        if any(c in string.ascii_uppercase for c in password):
            score += 1
        if any(c in string.digits for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1
        
        if score <= 3:
            return "Слабый"
        elif score <= 5:
            return "Средний"
        else:
            return "Надёжный"
    
    def check_hibp(self):
        try:
            sha1_hash = hashlib.sha1(self.password.encode()).hexdigest().upper()
            prefix = sha1_hash[:5]
            suffix = sha1_hash[5:]
            
            import urllib.request
            url = f"https://api.pwnedpasswords.com/range/{prefix}"
            req = urllib.request.Request(url, headers={"User-Agent": "PassWorlds-Password-Generator"})
            response = urllib.request.urlopen(req, timeout=5)
            data = response.read().decode()
            
            for line in data.split("\n"):
                if line.startswith(suffix):
                    count = int(line.split(":")[1])
                    self.hibp_count = count
                    self.hibp_label.configure(
                        text=f"⚠️ Найден в утечках {count:,} раз!",
                        text_color="red"
                    )
                    return
            
            self.hibp_count = 0
            self.hibp_label.configure(
                text="✓ Не найден в утечках",
                text_color="green"
            )
        except Exception as e:
            self.hibp_label.configure(text="", text_color="gray")
    
    def open_hibp_info(self):
        if self.hibp_count > 0:
            webbrowser.open(f"https://haveibeenpwned.com/")
    
    def copy_password(self):
        if self.password:
            pyperclip.copy(self.password)
            self.status_label.configure(text="Скопировано в буфер обмена!")
            self.after(2000, lambda: self.status_label.configure(text=""))
            
            # Save to history only if not already saved (check last 10)
            already_saved = any(p["password"] == self.password for p in self.password_history[:10])
            if not already_saved:
                strength = self.check_strength(self.password)
                self.password_history.insert(0, {
                    "password": self.password,
                    "length": len(self.password),
                    "strength": strength,
                    "timestamp": datetime.now().isoformat()
                })
                self.save_history()
    
    def open_history_window(self):
        self.reset_activity()
        if self.is_locked:
            return
        if self.has_master_password():
            self.show_history_auth()
        else:
            HistoryWindow(self, self.password_history)
    
    def show_history_auth(self):
        auth_win = ctk.CTkToplevel(self)
        auth_win.title("Подтверждение")
        auth_win.geometry("300x150")
        auth_win.resizable(False, False)
        auth_win.transient(self)
        
        ctk.CTkLabel(auth_win, text="Введите мастер-пароль:", font=ctk.CTkFont(size=14)).pack(pady=20)
        
        password_entry = ctk.CTkEntry(auth_win, show="*", width=200)
        password_entry.pack(pady=10)
        
        def try_show():
            if self.verify_master_password(password_entry.get()):
                auth_win.destroy()
                self.last_activity = datetime.now()
                HistoryWindow(self, self.password_history)
            else:
                ctk.CTkMessagebox(title="Ошибка", message="Неверный пароль!", icon="cancel")
        
        ctk.CTkButton(auth_win, text="Показать", command=try_show, width=100).pack(pady=10)
        password_entry.focus()
        auth_win.bind("<Return>", lambda e: try_show())
    
    def open_settings_window(self):
        SettingsWindow(self)
    
    def reset_to_defaults(self):
        self.settings = {
            "theme": "light",
            "color_theme": "Синий",
            "default_length": 16,
            "use_upper": True,
            "use_lower": True,
            "use_digits": True,
            "use_special": True,
            "auto_check_hibp": True
        }
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        self.apply_color_theme("Синий")
        self.save_settings()
        
        self.length_slider.set(16)
        self.uppercase_var.set(True)
        self.lowercase_var.set(True)
        self.digits_var.set(True)
        self.special_var.set(True)
        
        self.password_entry.configure(state="normal")
        self.password_entry.delete(0, "end")
        self.password_entry.configure(state="readonly")
        self.password = ""
        self.copy_btn.configure(state="disabled")
        
        self.strength_label.configure(text="")
        self.hibp_label.configure(text="")
        self.entropy_label.configure(text="")

class HistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, history):
        super().__init__(parent)
        
        self.title("История паролей")
        self.geometry("500x400")
        self.resizable(True, True)
        
        self.history = history
        
        self.textbox = ctk.CTkTextbox(self, font=ctk.CTkFont(size=12))
        self.textbox.pack(pady=10, padx=10, fill="both", expand=True)
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=10, padx=10, fill="x")
        
        clear_btn = ctk.CTkButton(
            btn_frame,
            text="Очистить историю",
            command=self.clear_history,
            fg_color="red",
            hover_color="darkred"
        )
        clear_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(
            btn_frame,
            text="Экспорт в файл",
            command=self.export_history
        )
        export_btn.pack(side="left", padx=5)
        
        self.update_display()
    
    def update_display(self):
        self.textbox.delete("1.0", "end")
        
        if not self.history:
            self.textbox.insert("1.0", "История пуста")
            return
        
        for i, item in enumerate(self.history[:50], 1):
            ts = datetime.fromisoformat(item["timestamp"]).strftime("%d.%m.%Y %H:%M")
            strength_color = {"Слабый": "🔴", "Средний": "🟡", "Надёжный": "🟢"}.get(item["strength"], "")
            self.textbox.insert("end", f"{i}. [{ts}] {strength_color} ({item['length']} символов)\n")
            self.textbox.insert("end", f"   {item['password']}\n\n")
    
    def clear_history(self):
        result = ctk.CTkInputDialog(
            text="Введите 'да' для подтверждения:",
            title="Очистить историю"
        ).get_input()
        if result and result.lower() == "да":
            self.history.clear()
            parent = self.master
            parent.password_history = []
            parent.save_history()
            self.update_display()
    
    def export_history(self):
        if not self.history:
            return
        
        filename = f"passworlds_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write("PassWorlds - История экспорта\n")
                f.write(f"Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n")
                f.write("=" * 50 + "\n\n")
                for i, item in enumerate(self.history, 1):
                    ts = datetime.fromisoformat(item["timestamp"]).strftime("%d.%m.%Y %H:%M")
                    f.write(f"{i}. [{ts}] - {item['strength']} ({item['length']} символов)\n")
                    f.write(f"   {item['password']}\n\n")
            ctk.CTkMessagebox(
                title="Успех",
                message=f"История экспортирована в {filename}",
                icon="check"
            )
        except Exception as e:
            ctk.CTkMessagebox(
                title="Ошибка",
                message=f"Ошибка экспорта: {str(e)}",
                icon="cancel"
            )

class SettingsWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.title("Настройки")
        self.geometry("380x520")
        self.resizable(True, True)
        
        self.parent = parent
        self.color_buttons = []
        
        self.setup_ui()
    
    def setup_ui(self):
        theme_frame = ctk.CTkFrame(self)
        theme_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(theme_frame, text="Тема:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
        
        self.theme_var = ctk.StringVar(value=self.parent.settings["theme"])
        theme_menu = ctk.CTkOptionMenu(
            theme_frame,
            values=["dark", "light", "system"],
            variable=self.theme_var
        )
        self.color_buttons.append(theme_menu)
        theme_menu.pack(pady=2, padx=20, fill="x")
        
        color_frame = ctk.CTkFrame(self)
        color_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(color_frame, text="Цвет кнопок:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
        
        color_eng_to_rus = {
            "blue": "Синий", "cyan": "Голубой", "red": "Красный",
            "pink": "Розовый", "green": "Зелёный", "lime": "Салатовый", "purple": "Фиолетовый"
        }
        saved_color = self.parent.settings.get("color_theme", "Синий")
        if saved_color in color_eng_to_rus:
            saved_color = color_eng_to_rus[saved_color]
        elif saved_color not in ["Синий", "Голубой", "Красный", "Розовый", "Зелёный", "Салатовый", "Фиолетовый"]:
            saved_color = "Синий"
        self.color_var = ctk.StringVar(value=saved_color)
        color_menu = ctk.CTkOptionMenu(
            color_frame,
            values=["Синий", "Голубой", "Красный", "Розовый", "Зелёный", "Салатовый", "Фиолетовый"],
            variable=self.color_var,
            command=self.change_color
        )
        self.color_buttons.append(color_menu)
        color_menu.pack(pady=2, padx=20, fill="x")
        
        options_frame = ctk.CTkFrame(self)
        options_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(options_frame, text="Опции:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
        
        self.hibp_var = ctk.BooleanVar(value=self.parent.settings.get("auto_check_hibp", True))
        hibp_cb = ctk.CTkCheckBox(
            options_frame,
            text="Автопроверка утечек (Have I Been Pwned)",
            variable=self.hibp_var
        )
        self.color_buttons.append(hibp_cb)
        hibp_cb.pack(pady=2, anchor="w", padx=10)
        
        master_frame = ctk.CTkFrame(self)
        master_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(master_frame, text="Мастер-пароль:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
        
        self.master_var = ctk.BooleanVar(value=self.parent.has_master_password())
        master_cb = ctk.CTkCheckBox(
            master_frame,
            text="Включить мастер-пароль",
            variable=self.master_var,
            command=self.toggle_master_password
        )
        master_cb.pack(pady=2, anchor="w", padx=10)
        
        self.master_entry = ctk.CTkEntry(
            master_frame,
            placeholder_text="Введите новый мастер-пароль",
            show="*",
            state="disabled"
        )
        self.master_entry.pack(pady=2, padx=10, fill="x")
        
        self.master_entry_confirm = ctk.CTkEntry(
            master_frame,
            placeholder_text="Подтвердите мастер-пароль",
            show="*",
            state="disabled"
        )
        self.master_entry_confirm.pack(pady=2, padx=10, fill="x")
        
        if self.parent.has_master_password():
            self.master_entry.configure(state="normal", placeholder_text="Оставьте пустым чтобы не менять")
            self.master_entry_confirm.configure(state="normal", placeholder_text="Оставьте пустым чтобы не менять")
        
        self.toggle_master_password()
        
        timeout_frame = ctk.CTkFrame(self)
        timeout_frame.pack(pady=10, padx=20, fill="x")
        
        ctk.CTkLabel(timeout_frame, text="Автоблокировка:", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(10, 2))
        
        self.timeout_var = ctk.IntVar(value=self.parent.settings.get("auto_lock_timeout", 5))
        timeout_menu = ctk.CTkOptionMenu(
            timeout_frame,
            values=["0", "1", "5", "10", "15", "30"],
            variable=self.timeout_var
        )
        timeout_menu.pack(pady=2, padx=20, fill="x")
        
        ctk.CTkLabel(timeout_frame, text="минут (0 = выкл)", font=ctk.CTkFont(size=11)).pack(pady=(0, 5))
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", padx=20)
        
        apply_btn = ctk.CTkButton(
            btn_frame,
            text="Применить",
            command=self.apply_and_close,
            width=90,
            height=40,
            fg_color="#27ae60",
            hover_color="#1e8449"
        )
        apply_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        cancel_btn = ctk.CTkButton(
            btn_frame,
            text="Отмена",
            command=self.cancel_and_close,
            width=90,
            height=40,
            fg_color="#c0392b",
            hover_color="#a93226"
        )
        cancel_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        reset_btn = ctk.CTkButton(
            btn_frame,
            text="Сброс",
            command=self.reset_settings,
            width=90,
            height=40,
            fg_color="gray",
            hover_color="darkgray"
        )
        reset_btn.pack(side="left", padx=5, fill="x", expand=True)
        apply_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        self.change_color(self.parent.settings["color_theme"], apply_to_parent=False)
    
    def toggle_master_password(self):
        if self.master_var.get():
            self.master_entry.configure(state="normal")
            self.master_entry_confirm.configure(state="normal")
        else:
            self.master_entry.configure(state="disabled")
            self.master_entry_confirm.configure(state="disabled")
    
    def change_color(self, color_name, apply_to_parent=True):
        color_map = {
            "Синий": ("#3b8ed0", "#1f6aa5"),
            "Голубой": ("#00a8cc", "#007a99"),
            "Красный": ("#e74c3c", "#c0392b"),
            "Розовый": ("#e91e8a", "#c01774"),
            "Зелёный": ("#27ae60", "#1e8449"),
            "Салатовый": ("#8bc34a", "#689f38"),
            "Фиолетовый": ("#9b59b6", "#8e44ad")
        }
        colors = color_map.get(color_name, color_map["Синий"])
        
        for widget in self.color_buttons:
            try:
                widget_type = type(widget).__name__
                if widget_type == "CTkOptionMenu":
                    widget.configure(fg_color=colors[0], button_color=colors[0], button_hover_color=colors[1])
                elif widget_type == "CTkCheckBox":
                    widget.configure(fg_color=colors[0], hover_color=colors[1])
            except:
                pass
        
        if apply_to_parent:
            self.parent.apply_color_theme(color_name)
    
    def reset_settings(self):
        DEFAULT_THEME = "light"
        DEFAULT_COLOR = "Синий"
        
        self.theme_var.set(DEFAULT_THEME)
        self.color_var.set(DEFAULT_COLOR)
        self.hibp_var.set(True)
        self.change_color(DEFAULT_COLOR, apply_to_parent=False)
        
        self.parent.settings["theme"] = DEFAULT_THEME
        self.parent.settings["color_theme"] = DEFAULT_COLOR
        self.parent.settings["auto_check_hibp"] = True
        self.parent.settings["use_upper"] = True
        self.parent.settings["use_lower"] = True
        self.parent.settings["use_digits"] = True
        self.parent.settings["use_special"] = True
        
        ctk.set_appearance_mode(DEFAULT_THEME)
        self.parent.apply_color_theme(DEFAULT_COLOR)
        
        self.parent.uppercase_var.set(True)
        self.parent.lowercase_var.set(True)
        self.parent.digits_var.set(True)
        self.parent.special_var.set(True)
        self.parent.custom_password_var.set(False)
        self.parent.toggle_custom_password()
        
        self.parent.save_settings()
    
    def cancel_and_close(self):
        self.destroy()
    
    def apply_and_close(self):
        color_name = self.color_var.get()
        
        self.parent.settings["theme"] = self.theme_var.get()
        self.parent.settings["color_theme"] = color_name
        self.parent.settings["auto_check_hibp"] = self.hibp_var.get()
        self.parent.settings["auto_lock_timeout"] = self.timeout_var.get()
        
        # Handle master password
        if self.master_var.get():
            new_pass = self.master_entry.get()
            confirm_pass = self.master_entry_confirm.get()
            if new_pass or self.parent.has_master_password():
                if new_pass != confirm_pass:
                    ctk.CTkMessagebox(title="Ошибка", message="Пароли не совпадают!", icon="cancel")
                    return
                if new_pass:
                    self.parent.save_master_password(new_pass)
                elif not new_pass and self.parent.has_master_password():
                    pass  # Keep existing password
        else:
            if self.parent.has_master_password():
                self.parent.save_master_password("")
        
        ctk.set_appearance_mode(self.parent.settings["theme"])
        self.parent.apply_color_theme(color_name)
        self.parent.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
