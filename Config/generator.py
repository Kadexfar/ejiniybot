import os 
import webbrowser
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

# Абсолютный путь к папке Config в корне проекта
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))  # Получаем путь к корню проекта
CONFIG_DIR = os.path.join(ROOT_DIR, "Config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.py")

# Замени на свой Client ID
CLIENT_ID = 'gp762nuuoqcoxypju8c569th9wz7q5'

# Все доступные права (scopes) для бота
SCOPES = [
    "analytics:read:extensions",
    "analytics:read:games",
    "bits:read",
    "channel:edit:commercial",
    "channel:manage:broadcast",
    "channel:manage:moderators",
    "channel:manage:polls",
    "channel:manage:predictions",
    "channel:manage:redemptions",
    "channel:manage:schedule",
    "channel:manage:vips",
    "channel:moderate",
    "channel:read:charity",
    "channel:read:editors",
    "channel:read:goals",
    "channel:read:hype_train",
    "channel:read:polls",
    "channel:read:predictions",
    "channel:read:redemptions",
    "channel:read:subscriptions",
    "clips:edit",
    "moderation:read",
    "moderator:manage:announcements",
    "moderator:manage:banned_users",
    "moderator:manage:chat_messages",
    "moderator:manage:chat_settings",
    "moderator:read:chatters",
    "moderator:read:followers",
    "user:edit",
    "user:manage:blocked_users",
    "user:manage:chat_color",
    "user:read:blocked_users",
    "user:read:broadcast",
    "user:read:email",
    "user:read:follows",
    "user:read:subscriptions",
    "whispers:read",
    "whispers:edit"
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
            const fragment = new URLSearchParams(window.location.hash.substring(1));
            const accessToken = fragment.get("access_token");

            if (accessToken) {
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
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)

        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()

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
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            f.write(f"PASS = 'oauth:{token}'\n")
        print("✅ Файл Config/config.py создан, токен сохранен!")

# HTTP-сервер для перехвата access_token
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/token?access_token="):
            token = self.path.split("access_token=")[-1].split("&")[0]
            print("\n✅ Получен access_token:", token)

            save_token_to_config(token)

            self.send_response(302)
            self.send_header("Location", "http://localhost:5000")  # Адрес страницы бота
            self.end_headers()

            threading.Thread(target=self.server.shutdown).start()
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

# Функция запуска сервера
def get_oauth_token():
    server = HTTPServer(("localhost", 8080), OAuthHandler)
    print("🌍 Локальный сервер запущен на http://localhost:8080")

    webbrowser.open(oauth_url)
    print("🌐 Открываем браузер для авторизации...")

    server.serve_forever()

# Запускаем процесс получения токена
if __name__ == "__main__":
    get_oauth_token()