import random
import string
import pyperclip
import secrets
import argparse
import json
import hashlib
import sys
import os

APP_DIR = os.path.join(os.path.expanduser("~"), ".passworlds")
os.makedirs(APP_DIR, exist_ok=True)
CONFIG_FILE = os.path.join(APP_DIR, "cli_settings.json")

def load_config():
    default = {"default_length": 16, "use_upper": True, "use_lower": True, "use_digits": True, "use_special": True}
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return {**default, **json.load(f)}
    return default

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

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

def calculate_entropy(length: int, chars: str) -> float:
    if chars:
        return length * (len(chars) ** 0.5)
    return 0

def check_hibp(password: str) -> tuple:
    try:
        sha1_hash = hashlib.sha1(password.encode()).hexdigest().upper()
        prefix = sha1_hash[:5]
        suffix = sha1_hash[5:]
        
        import urllib.request
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        req = urllib.request.Request(url, headers={"User-Agent": "PassWorlds-CLI"})
        response = urllib.request.urlopen(req, timeout=5)
        data = response.read().decode()
        
        for line in data.split("\n"):
            if line.startswith(suffix):
                count = int(line.split(":")[1])
                return True, count
        return False, 0
    except Exception:
        return None, 0

def print_help():
    print("""
PassWorlds CLI - Генератор паролей
==================================

Использование: python password_generator.py [опции]

Опции:
  -l, --length N        Длина пароля (по умолчанию: 16)
  -u, --no-upper        Без заглавных букв
  -L, --no-lower        Без строчных букв  
  -d, --no-digits       Без цифр
  -s, --no-special      Без специальных символов
  -c, --count N         Количество паролей (по умолчанию: 1)
  -o, --output FILE     Сохранить в файл
  --check               Проверить пароль на утечки
  --export              Экспортировать настройки
  --import              Импортировать настройки
  -h, --help            Показать эту справку

Примеры:
  python password_generator.py
  python password_generator.py -l 32 -s
  python password_generator.py -c 10 -o passwords.txt
""")

def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("-l", "--length", type=int, default=None)
    parser.add_argument("-u", "--no-upper", action="store_true")
    parser.add_argument("-L", "--no-lower", action="store_true")
    parser.add_argument("-d", "--no-digits", action="store_true")
    parser.add_argument("-s", "--no-special", action="store_true")
    parser.add_argument("-c", "--count", type=int, default=1)
    parser.add_argument("-o", "--output", type=str)
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--export", action="store_true")
    parser.add_argument("--import", dest="import_settings", action="store_true")
    parser.add_argument("-h", "--help", action="store_true")
    parser.add_argument("password_check", nargs="?", default=None)
    
    args = parser.parse_args()
    
    if args.help:
        print_help()
        return
    
    config = load_config()
    
    if args.export:
        print(f"Экспорт настроек в {CONFIG_FILE}")
        save_config(config)
        print("Готово!")
        return
    
    if args.import_settings:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE) as f:
                config = json.load(f)
            print("Настройки импортированы:")
            print(json.dumps(config, indent=2))
        else:
            print("Файл настроек не найден")
        return
    
    length = args.length if args.length else config["default_length"]
    length = max(4, min(128, length))
    
    use_upper = not args.no_upper if args.no_upper else config["use_upper"]
    use_lower = not args.no_lower if args.no_lower else config["use_lower"]
    use_digits = not args.no_digits if args.no_digits else config["use_digits"]
    use_special = not args.no_special if args.no_special else config["use_special"]
    
    passwords = []
    
    for i in range(args.count):
        pwd = generate_password(length, use_upper, use_lower, use_digits, use_special)
        passwords.append(pwd)
    
    output_file = None
    if args.output:
        try:
            output_file = open(args.output, "w", encoding="utf-8")
        except Exception as e:
            print(f"Ошибка открытия файла: {e}")
            return
    
    for i, pwd in enumerate(passwords, 1):
        strength = check_password_strength(pwd)
        entropy = calculate_entropy(length, 
            (string.ascii_uppercase if use_upper else "") +
            (string.ascii_lowercase if use_lower else "") +
            (string.digits if use_digits else "") +
            (string.punctuation if use_special else ""))
        
        prefix = f"[{i}/{args.count}] " if args.count > 1 else ""
        
        if args.password_check or (args.check and not args.password_check):
            pwd_to_check = pwd if args.password_check else pwd
            leaked, count = check_hibp(pwd_to_check)
            if leaked is None:
                hibp_info = "(проверка недоступна)"
            elif leaked:
                hibp_info = f"(УТЕЧКА: найден {count:,} раз!)"
            else:
                hibp_info = "(не найден в утечках)"
        else:
            hibp_info = ""
        
        line = f"{prefix}{pwd} | {strength} | {entropy:.0f} бит {hibp_info}"
        print(line)
        
        if output_file:
            output_file.write(line + "\n")
    
    if output_file:
        output_file.close()
        print(f"\nСохранено в {args.output}")
    
    if args.count == 1 and not args.output and not args.password_check and not args.check:
        copy = input("\nКопировать в буфер обмена? (Д/н): ").lower()
        if copy != 'н':
            pyperclip.copy(passwords[0])
            print("Скопировано!")

if __name__ == "__main__":
    main()
