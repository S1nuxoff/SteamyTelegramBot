# app/localization.py

import json

# Функция для загрузки локализации
def load_localization():
    with open('locale/localization.json', 'r', encoding='utf-8') as f:
        localization = json.load(f)
    return localization

# Инициализация локализации
localization = load_localization()

# Функция для получения текста на основе языка и ключа
def get_text(language, key):
    keys = key.split('.')
    text = localization.get(language, {})
    for k in keys:
        text = text.get(k, '')
        if not text:
            break
    return text
