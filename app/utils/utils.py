from main import  localization

def get_text(language, key):

    keys = key.split('.')
    text = localization.get(language, {})
    for k in keys:
        text = text.get(k, '')
        if not text:
            break
    return text
