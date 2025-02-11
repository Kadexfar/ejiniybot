from flask import Flask, render_template, request, redirect, url_for
import json
import os

app = Flask(__name__)

CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'Config')
COMMANDS_FILE = os.path.join(CONFIG_DIR, 'commands.json')
BLACKLIST_FILE = os.path.join(CONFIG_DIR, 'blacklist.txt')

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

# Функция для удаления нескольких команд
def remove_multiple_commands_from_file(commands_to_remove):
    commands = load_commands()
    for command in commands_to_remove:
        if command in commands:
            del commands[command]
    with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
        json.dump(commands, f, ensure_ascii=False, indent=4)

# Функция для удаления нескольких запрещенных слов
def remove_multiple_blacklist_words_from_file(words_to_remove):
    blacklist = load_blacklist()
    for word in words_to_remove:
        if word in blacklist:
            blacklist.remove(word)
    with open(BLACKLIST_FILE, "w", encoding="utf-8") as f:
        f.writelines([line + '\n' for line in blacklist])

# Страница с командами и запрещенными словами
@app.route('/')
def index():
    return render_template('index.html')

# Страница с командами
@app.route('/commands')
def commands_page():
    commands = load_commands()
    return render_template('commands.html', commands=commands)

# Страница с запрещенными словами
@app.route('/blacklist')
def blacklist_page():
    blacklist = load_blacklist()
    return render_template('blacklist.html', blacklist=blacklist)

# Страница добавления команды
@app.route('/add_command', methods=['GET', 'POST'])
def add_command_page():
    if request.method == 'POST':
        command = request.form.get('command')
        response = request.form.get('response')

        # Запись команды в файл
        with open(COMMANDS_FILE, "r", encoding="utf-8") as f:
            commands = json.load(f)
        
        if command not in commands:
            commands[command] = response
            with open(COMMANDS_FILE, "w", encoding="utf-8") as f:
                json.dump(commands, f)
            return redirect(url_for('index'))  # Перенаправить на главную страницу
        else:
            flash("Эта команда уже существует!", "error")
            return redirect(url_for('add_command_page'))
    
    return render_template('add_command.html')

# Страница добавления запрещенного слова
@app.route('/add_blacklist_word', methods=['GET', 'POST'])
def add_blacklist_word_page():
    if request.method == 'POST':
        word = request.form.get('word')
        # Сохранить запрещенное слово в файл или базу данных
        return redirect(url_for('index'))  # Перенаправить на главную страницу
    return render_template('add_blacklist_word.html')

# Удаление нескольких команд
@app.route('/remove_multiple_commands', methods=['POST'])
def remove_multiple_commands():
    commands_to_remove = request.form.getlist('commands_to_remove')
    remove_multiple_commands_from_file(commands_to_remove)
    return redirect(url_for('commands_page'))

# Удаление нескольких запрещенных слов
@app.route('/remove_multiple_blacklist_words', methods=['POST'])
def remove_multiple_blacklist_words():
    words_to_remove = request.form.getlist('blacklist_to_remove')
    remove_multiple_blacklist_words_from_file(words_to_remove)
    return redirect(url_for('blacklist_page'))

if __name__ == '__main__':
    app.run(debug=True)