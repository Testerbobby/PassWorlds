import random
import string
import pyperclip
import secrets

def generate_password(length: int, use_upper: bool, use_lower: bool, 
                     use_digits: bool, use_special: bool) -> str:
    chars = ""
    if use_upper:
        chars += string.ascii_uppercase
    if use_lower:
        chars += string.ascii_lowercase
    if use_digits:
        chars += string.digits
    if use_special:
        chars += string.punctuation
    
    if not chars:
        chars = string.ascii_letters + string.digits
    
    return ''.join(secrets.choice(chars) for _ in range(length))

def check_password_strength(password: str) -> str:
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

def main():
    print("=" * 40)
    print("   Генератор безопасных паролей")
    print("=" * 40)
    
    try:
        length = int(input("\nДлина пароля (по умолчанию 16): ") or 16)
        length = max(4, min(128, length))
        
        print("\nНастройки символов:")
        use_upper = input("   Использовать заглавные буквы? (Д/н): ").lower() != 'н'
        use_lower = input("   Использовать строчные буквы? (Д/н): ").lower() != 'н'
        use_digits = input("   Использовать цифры? (Д/н): ").lower() != 'н'
        use_special = input("   Использовать специальные символы? (Д/н): ").lower() != 'н'
        
        password = generate_password(length, use_upper, use_lower, use_digits, use_special)
        strength = check_password_strength(password)
        
        print("\n" + "=" * 40)
        print(f"   Ваш пароль: {password}")
        print(f"   Надёжность: {strength}")
        print("=" * 40)
        
        if input("\nКопировать в буфер обмена? (Д/н): ").lower() != 'н':
            pyperclip.copy(password)
            print("   Пароль скопирован!")
            
    except ValueError:
        print("Ошибка: введите корректное число")

if __name__ == "__main__":
    main()
