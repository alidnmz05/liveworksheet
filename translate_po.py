import os
import polib
from deep_translator import GoogleTranslator

# language map
lang_map = {
    'en': 'en',
    'de': 'de',
    'es': 'es',
    'fr': 'fr',
    'it': 'it',
    'pt': 'pt',
    'ru': 'ru',
    'zh_Hans': 'zh-CN',
    'ko': 'ko',
    'ar': 'ar'
}

base_dir = '/Users/ismaildundar/Desktop/bitirmeProjesi/liveworksheet/locale'

for lang, g_lang in lang_map.items():
    po_file_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'django.po')
    if not os.path.exists(po_file_path):
        print(f"File not found: {po_file_path}")
        continue
    
    print(f"Processing {lang}...")
    po = polib.pofile(po_file_path)
    translator = GoogleTranslator(source='tr', target=g_lang)
    
    count = 0
    for entry in po.untranslated_entries():
        if not entry.msgid:
            continue
        try:
            # Handle special characters
            msgid = entry.msgid.replace("\\'", "'")
            translated = translator.translate(msgid)
            entry.msgstr = translated
            count += 1
        except Exception as e:
            print(f"Error translating '{entry.msgid}' to {lang}: {e}")
            
    po.save()
    print(f"Saved {lang} - {count} strings translated.")
