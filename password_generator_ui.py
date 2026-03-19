import customtkinter as ctk
import secrets
import string
import pyperclip
import hashlib
import json
import os
import webbrowser
import keyboard
from datetime import datetime

APP_DIR = os.path.join(os.path.expanduser("~"), ".passworlds")
os.makedirs(APP_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APP_DIR, "settings.json")
HISTORY_FILE = os.path.join(APP_DIR, "history.json")

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PassWorlds - Генератор паролей")
        self.geometry("550x750")
        self.resizable(False, False)
        
        self.password = ""
        self.password_history = []
        self.hibp_count = 0
        
        self.load_settings()
        self.load_history()
        
        color_rus_to_eng = {
            "Синий": "blue",
            "Голубой": "cyan",
            "Красный": "red",
            "Розовый": "pink",
            "Зелёный": "green",
            "Салатовый": "lime",
            "Фиолетовый": "purple"
        }
        ctk.set_appearance_mode(self.settings["theme"])
        eng_color = color_rus_to_eng.get(self.settings["color_theme"], "blue")
        ctk.set_default_color_theme(eng_color)
        
        self.setup_ui()
        self.bind_shortcuts()
    
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
            "master_password": "",
            "auto_check_hibp": True
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
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.settings, f, indent=2)
    
    def apply_color_theme(self, color_name):
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
        
        for btn in [self.settings_btn, self.history_btn, self.generate_btn, self.copy_btn]:
            btn.configure(fg_color=colors[0], hover_color=colors[1])
        
        self.length_slider.configure(button_color=colors[0], button_hover_color=colors[1])
        
        for cb in [self.uppercase_cb, self.lowercase_cb, self.digits_cb, self.special_cb]:
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
        self.title_label = ctk.CTkLabel(
            self, 
            text="PassWorlds - Генератор паролей",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=15)
        
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
    
    def bind_shortcuts(self):
        keyboard.add_hotkey("ctrl+g", self.generate_password)
        keyboard.add_hotkey("ctrl+h", self.open_history_window)
    
    def update_length_label(self, value):
        self.length_label.configure(text=f"Длина пароля: {int(value)}")
    
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
        
        self.password_history.insert(0, {
            "password": self.password,
            "length": length,
            "strength": strength,
            "timestamp": datetime.now().isoformat()
        })
        self.save_history()
        
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
    
    def open_history_window(self):
        HistoryWindow(self, self.password_history)
    
    def open_settings_window(self):
        SettingsWindow(self)

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
        self.geometry("350x350")
        self.resizable(False, False)
        
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
        
        self.color_var = ctk.StringVar(value=self.parent.settings["color_theme"])
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
        
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(pady=20, fill="x", padx=20)
        
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
        
        self.change_color(self.parent.settings["color_theme"], apply_to_parent=False)
    
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
        self.theme_var.set(self.parent.settings["theme"])
        self.color_var.set(self.parent.settings["color_theme"])
        self.hibp_var.set(self.parent.settings["auto_check_hibp"])
        self.change_color(self.parent.settings["color_theme"], apply_to_parent=False)
    
    def cancel_and_close(self):
        self.destroy()
    
    def apply_and_close(self):
        color_name = self.color_var.get()
        
        self.parent.settings["theme"] = self.theme_var.get()
        self.parent.settings["color_theme"] = color_name
        self.parent.settings["auto_check_hibp"] = self.hibp_var.get()
        
        ctk.set_appearance_mode(self.parent.settings["theme"])
        self.parent.apply_color_theme(color_name)
        self.parent.save_settings()
        self.destroy()

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
