import os
import subprocess
import sys

# Путь к requirements.txt
REQ_FILE = os.path.join(os.path.dirname(__file__), "requirements.txt")

def install_requirements():
    """ Устанавливает зависимости из requirements.txt """
    print("📦 Установка зависимостей...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", REQ_FILE], check=True)
    print("✅ Установка завершена!")

if __name__ == "__main__":
    install_requirements()