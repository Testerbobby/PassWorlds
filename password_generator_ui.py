import customtkinter as ctk
import secrets
import string
import pyperclip

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class PasswordGeneratorApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("PassWorlds - Генератор паролей")
        self.geometry("500x650")
        self.resizable(False, False)
        
        self.password = ""
        
        self.setup_ui()
    
    def setup_ui(self):
        self.title_label = ctk.CTkLabel(
            self, 
            text="🔐 Генератор паролей",
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.title_label.pack(pady=20)
        
        self.password_frame = ctk.CTkFrame(self)
        self.password_frame.pack(pady=10, padx=20, fill="x")
        
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            font=ctk.CTkFont(size=20),
            height=50,
            placeholder_text="Нажмите 'Сгенерировать'",
            state="readonly"
        )
        self.password_entry.pack(pady=10, padx=10, fill="x")
        
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.pack(pady=10, padx=20, fill="x")
        
        self.generate_btn = ctk.CTkButton(
            self.button_frame,
            text="Сгенерировать",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self.generate_password
        )
        self.generate_btn.pack(pady=5, fill="x")
        
        self.copy_btn = ctk.CTkButton(
            self.button_frame,
            text="📋 Копировать",
            font=ctk.CTkFont(size=14),
            height=40,
            command=self.copy_password,
            state="disabled"
        )
        self.copy_btn.pack(pady=5, fill="x")
        
        self.settings_frame = ctk.CTkFrame(self)
        self.settings_frame.pack(pady=15, padx=20, fill="x")
        
        self.length_label = ctk.CTkLabel(self.settings_frame, text="Длина пароля:", font=ctk.CTkFont(size=14))
        self.length_label.pack(pady=(15, 5))
        
        self.length_slider = ctk.CTkSlider(
            self.settings_frame,
            from_=4,
            to=64,
            number_of_steps=60,
            command=self.update_length_label
        )
        self.length_slider.set(16)
        self.length_slider.pack(pady=5, padx=20, fill="x")
        
        self.length_value_label = ctk.CTkLabel(
            self.settings_frame, 
            text="16", 
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.length_value_label.pack(pady=(0, 10))
        
        self.checkbox_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.checkbox_frame.pack(pady=10, padx=20)
        
        self.uppercase_var = ctk.BooleanVar(value=True)
        self.uppercase_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="A-Z Заглавные",
            variable=self.uppercase_var,
            font=ctk.CTkFont(size=14)
        )
        self.uppercase_cb.pack(pady=3, anchor="w")
        
        self.lowercase_var = ctk.BooleanVar(value=True)
        self.lowercase_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="a-z Строчные",
            variable=self.lowercase_var,
            font=ctk.CTkFont(size=14)
        )
        self.lowercase_cb.pack(pady=3, anchor="w")
        
        self.digits_var = ctk.BooleanVar(value=True)
        self.digits_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="0-9 Цифры",
            variable=self.digits_var,
            font=ctk.CTkFont(size=14)
        )
        self.digits_cb.pack(pady=3, anchor="w")
        
        self.special_var = ctk.BooleanVar(value=True)
        self.special_cb = ctk.CTkCheckBox(
            self.checkbox_frame,
            text="!@#$%^&* Спецсимволы",
            variable=self.special_var,
            font=ctk.CTkFont(size=14)
        )
        self.special_cb.pack(pady=3, anchor="w")
        
        self.strength_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=14)
        )
        self.strength_label.pack(pady=10)
        
        self.status_label = ctk.CTkLabel(
            self,
            text="",
            text_color="green",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(pady=5)
    
    def update_length_label(self, value):
        self.length_value_label.configure(text=str(int(value)))
    
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
    
    def check_strength(self, password):
        score = 0
        if len(password) >= 8:
            score += 1
        if len(password) >= 12:
            score += 1
        if any(c in string.ascii_lowercase for c in password):
            score += 1
        if any(c in string.ascii_uppercase for c in password):
            score += 1
        if any(c in string.digits for c in password):
            score += 1
        if any(c in string.punctuation for c in password):
            score += 1
        
        if score <= 2:
            return "Слабый"
        elif score <= 4:
            return "Средний"
        else:
            return "Надёжный"
    
    def copy_password(self):
        if self.password:
            pyperclip.copy(self.password)
            self.status_label.configure(text="✓ Скопировано в буфер обмена!")
            self.after(2000, lambda: self.status_label.configure(text=""))

if __name__ == "__main__":
    app = PasswordGeneratorApp()
    app.mainloop()
