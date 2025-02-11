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

# Функция обработки сообщений
def handle_message(sock, raw_message):
    try:
        if "PRIVMSG" in raw_message:
            parts = raw_message.split(":", 2)
            if len(parts) < 3:
                print("Ошибка: не удалось разобрать сообщение.")
                return

            username = parts[1].split("!")[0]
            message_content = parts[2].strip().lower()

            print(f"{username}: {message_content}")

            # Загружаем список запрещенных слов и другие данные
            blacklist = load_blacklist()
            responses = load_responses()

            # Проверяем запрещенные слова (ищем часть слова в сообщении)
            for bad_word in blacklist:
                if bad_word in message_content:  # Проверяем, есть ли слово как часть другого слова
                    if random.random() < 0.05:  # 5% шанс на тайм-аут
                        sock.send(f"PRIVMSG {CHAN} :/timeout {username} 10\r\n".encode('utf-8'))
                        print(f"Бот наложил тайм-аут на {username} за слово: {bad_word}")
                    break  # Останавливаем обработку, если слово найдено, чтобы не отправлять ответ
            else:
                # Если запрещенное слово не найдено, проверяем команды
                commands = load_commands()
                if message_content in commands:
                    response = commands[message_content].replace("{user}", username)
                    send_message(sock, response)
                    print(f"Бот ответил: {response}")

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
    secure_sock.send(f"JOIN {CHAN}\r\n".encode('utf-8'))
    
    print(f"✅ Бот успешно зашел в канал {CHAN}.")

    return secure_sock

# Основной цикл для прослушивания сообщений
def main():
    sock = connect()

    while True:
        try:
            data = sock.recv(1024).decode('utf-8')

            # Убираем вывод "Received data" для серверных сообщений
            if re.match(r"^:tmi.twitch.tv", data):
                continue  # Пропускаем сообщения от сервера

            print(f"Received data: {data}")

            if data.startswith("PING"):
                sock.send("PONG :tmi.twitch.tv\r\n".encode('utf-8'))
                print("PONG отправлен для поддержания соединения.")

            if "PRIVMSG" in data:
                handle_message(sock, data)

            time.sleep(0.1)

        except Exception as e:
            print(f"Ошибка: {e}")
            break

    sock.close()

if __name__ == "__main__":
    main()