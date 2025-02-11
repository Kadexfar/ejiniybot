import subprocess
import time
import os

# Пути к файлам
GENERATOR = os.path.join("config", "generator.py")
WEB_SERVER = os.path.join("Main", "web_server.py")
TWITCH_BOT = os.path.join("Main", "twitch_bot.py")

def run_script(script):
    """ Функция для запуска скрипта """
    return subprocess.Popen(["python", script])

print("▶ Запуск generator.py...")
subprocess.run(["python", GENERATOR], check=True)

print("▶ Запуск web_server.py...")
web_server = run_script(WEB_SERVER)

time.sleep(3)  # Ждём запуск сервера

print("▶ Запуск twitch_bot.py...")
twitch_bot = run_script(TWITCH_BOT)

try:
    twitch_bot.wait()
except KeyboardInterrupt:
    print("⏹ Остановка всех процессов...")
    web_server.terminate()
    twitch_bot.terminate()