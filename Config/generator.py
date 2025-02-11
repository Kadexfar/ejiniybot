import os
import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Абсолютный путь к папке Config в корне проекта
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Получаем путь к корню проекта
CONFIG_DIR = os.path.join(ROOT_DIR, "Config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.py")

# Замени на свой Client ID
CLIENT_ID = '8pet2l4yk0762h60s902ochjsajnad'

# Все доступные права (scopes) для бота
SCOPES = [
    "bits:read",
    "channel:read:redemptions",
    "channel:manage:redemptions",
    "channel:moderate",
    "chat:edit",
    "chat:read",
    "moderator:read:followers",
    "moderator:manage:announcements",
    "moderator:manage:banned_users",
    "moderator:manage:chat_messages",
    "user:read:email"
]

# Генерация OAuth URL
oauth_url = (
    f"https://id.twitch.tv/oauth2/authorize"
    f"?client_id={CLIENT_ID}"
    f"&redirect_uri=http://localhost:8080"
    f"&response_type=token"
    f"&scope={'+'.join(SCOPES)}"
)

# HTML с JavaScript для извлечения токена
HTML_PAGE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Получение Access Token</title>
    <script>
        window.onload = function() {
            // Извлекаем access_token из URL
            const fragment = new URLSearchParams(window.location.hash.substring(1));
            const accessToken = fragment.get("access_token");

            if (accessToken) {
                // Перенаправляем токен на сервер
                window.location.href = "/token?access_token=" + accessToken;
            } else {
                document.body.innerHTML = "<h1>Ошибка! Access Token не найден.</h1>";
            }
        };
    </script>
</head>
<body>
    <h1>Идет обработка токена...</h1>
</body>
</html>
"""

# Функция для сохранения токена в config.py
def save_token_to_config(token):
    try:
        # Проверка существования папки Config и создание её при необходимости
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        # Чтение файла config.py
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

        # Перезапись с токеном
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            updated = False
            for line in lines:
                if line.startswith("PASS ="):
                    f.write(f"PASS = 'oauth:{token}'\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"\nPASS = 'oauth:{token}'\n")

        print("✅ Токен успешно сохранен в Config/config.py!")
    except FileNotFoundError:
        # Если файл не существует, создаём его
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"PASS = 'oauth:{token}'\n")
        print("✅ Файл Config/config.py создан, токен сохранен!")

# HTTP-сервер для перехвата access_token
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/token?access_token="):
            # Извлекаем токен из URL
            token = self.path.split("access_token=")[-1].split("&")[0]
            print("\n✅ Получен access_token:", token)

            # Сохраняем токен в config.py
            save_token_to_config(token)

            # Отправляем HTML-ответ с перенаправлением на страницу бота
            self.send_response(302)
            self.send_header("Location", "http://localhost:5000")  # Адрес страницы бота
            self.end_headers()

            # Завершаем сервер в отдельном потоке
            threading.Thread(target=self.server.shutdown).start()

        else:
            # Отправляем HTML с JavaScript
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

# Функция запуска сервера
def get_oauth_token():
    server = HTTPServer(("localhost", 8080), OAuthHandler)
    print("🌍 Локальный сервер запущен на http://localhost:8080")

    # Открываем браузер
    webbrowser.open(oauth_url)
    print("🌐 Открываем браузер для авторизации...")

    # Запускаем сервер (он завершится сам после получения токена)
    server.serve_forever()

# Запускаем процесс получения токена
if __name__ == "__main__":
    get_oauth_token()