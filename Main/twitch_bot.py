import sys
import os
import socket
import ssl
import time
import json
import random
import re  # Для регулярных выражений

# Путь к папке Config
CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'Config')

# Путь к файлу config.py в папке Config
config_path = os.path.join(CONFIG_DIR, 'Config')
sys.path.insert(0, config_path)
from config import NICK, PASS, CHAN

# Путь к конфигурационным файлам
COMMANDS_FILE = os.path.join(CONFIG_DIR, 'commands.json')
BLACKLIST_FILE = os.path.join(CONFIG_DIR, 'blacklist.txt')
RESPONSES_FILE = os.path.join(CONFIG_DIR, 'responses.json')

# Данные для подключения к Twitch IRC
HOST = 'irc.chat.twitch.tv'
PORT = 6697


# Функция загрузки команд
def load_commands():
    try:
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Функция загрузки запрещенных слов
def load_blacklist():
    try:
        with open(BLACKLIST_FILE, "r", encoding="utf-8") as f:
            return [line.strip().lower() for line in f.readlines()]
    except FileNotFoundError:
        return []

# Функция загрузки возможных ответов
def load_responses():
    try:
        with open(RESPONSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# Функция для отправки сообщений в чат
def send_message(sock, message):
    sock.send(f"PRIVMSG {CHAN} :{message}\r\n".encode('utf-8'))

# Функция для наложения таймаута
def timeout_user(sock, username):
    """С шансом 5% накладывает таймаут 10 секунд на пользователя."""
    if random.randint(1, 100) <= 101:  # 5% шанс
        timeout_command = f"PRIVMSG {CHAN} :.timeout {username} 10\r\n"
        print(f"Отправляю команду: {timeout_command.strip()}")  # Вывод в консоль
        sock.send(timeout_command.encode('utf-8'))
        return True
    return False

# Функция обработки сообщений
def handle_message(sock, raw_message):
    if "PRIVMSG" in raw_message:
        try:
            parts = raw_message.split(":", 2)
            if len(parts) < 3:
                return

            username = parts[1].split("!")[0]
            message_content = parts[2].strip().lower()

            print(f"{username}: {message_content}")

            # Загружаем команды и запрещенные слова
            commands = load_commands()
            blacklist = load_blacklist()

            # Проверяем команды
            if message_content in commands:
                response = commands[message_content].replace("{user}", username)
                send_message(sock, response)
                print(f"Бот ответил: {response}")

            # Проверяем запрещенные слова
            for bad_word in blacklist:
                if bad_word in message_content:
                    if timeout_user(sock, username):  # Если наложен таймаут, бот молчит
                        print(f"Бот наложил таймаут на {username} за слово: {bad_word}")
                    break  # Останавливаем проверку после первого найденного слова

        except IndexError as e:
            print(f"Ошибка при разборе сообщения: {e}")

# Подключение к Twitch IRC
def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    secure_sock = context.wrap_socket(sock, server_hostname=HOST)

    secure_sock.connect((HOST, PORT))
    print("✅ Подключение установлено!")

    secure_sock.send(f"PASS {PASS}\r\n".encode('utf-8'))
    secure_sock.send(f"NICK {NICK}\r\n".encode('utf-8'))
    secure_sock.send(f"JOIN #{CHAN}\r\n".encode('utf-8'))

    print(f"✅ Бот успешно зашел в канал {CHAN}.")

    return secure_sock

# Основной цикл для прослушивания сообщений
def main():
    sock = connect()
    while True:
        try:
            data = sock.recv(1024).decode('utf-8')
            print("DEBUG: Received data:", data)  # Эта строка покажет все полученные данные

            if data.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                print("DEBUG: Отправлен PONG.")

            if "PRIVMSG" in data:
                handle_message(sock, data)

            time.sleep(0.1)
        except Exception as e:
            print(f"Ошибка: {e}")
            break
    sock.close()

if __name__ == "__main__":
    main()