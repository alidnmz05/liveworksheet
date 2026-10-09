import os
import polib
from deep_translator import GoogleTranslator
import time

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
    
    untranslated = po.untranslated_entries()
    if not untranslated:
        print(f"No untranslated entries for {lang}.")
        continue

    # Prepare batch
    msgids = []
    for entry in untranslated:
        msgids.append(entry.msgid.replace("\\'", "'"))
        
    try:
        # translate batch
        print(f"Translating {len(msgids)} strings for {lang}...")
        translated_list = translator.translate_batch(msgids)
        
        # update po file
        for entry, trans in zip(untranslated, translated_list):
            entry.msgstr = trans if trans else entry.msgid
            
        po.save()
        print(f"Saved {lang} - {len(msgids)} strings translated.")
        
    except Exception as e:
        print(f"Error translating batch to {lang}: {e}")
        
    time.sleep(1) # small pause between languages to avoid rate limiting
