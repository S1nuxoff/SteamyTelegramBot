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
    """
    Получает локализованный текст на основе языка и ключа.

    :param language: Код языка (например, 'en', 'ru', 'uk', 'tt')
    :param key: Ключ строки, разделённый точками (например, 'buttons.BACK_BUTTON')
    :return: Локализованный текст или пустая строка, если ключ не найден
    """
    keys = key.split('.')
    text = localization.get(language, {})
    for k in keys:
        text = text.get(k, '')
        if not text:
            break
    return text
