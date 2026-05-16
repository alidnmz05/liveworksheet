import os
import polib
from deep_translator import GoogleTranslator
import time

lang_map = {
    'en': 'en', 'de': 'de', 'es': 'es', 'fr': 'fr', 'it': 'it',
    'pt': 'pt', 'ru': 'ru', 'zh_Hans': 'zh-CN', 'ko': 'ko', 'ar': 'ar'
}

base_dir = '/Users/ismaildundar/Desktop/bitirmeProjesi/liveworksheet/locale'

for lang, g_lang in lang_map.items():
    po_file_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'django.po')
    if not os.path.exists(po_file_path):
        continue
    
    print(f"Processing {lang}...")
    po = polib.pofile(po_file_path)
    translator = GoogleTranslator(source='tr', target=g_lang)
    
    untranslated = po.untranslated_entries()
    if not untranslated:
        print(f"No untranslated entries for {lang}.")
        continue

    # Prepare single batch string
    msgids = [entry.msgid.replace("\\'", "'") for entry in untranslated]
    
    batch_text = " ||| ".join(msgids)
    
    try:
        print(f"Translating {len(msgids)} strings for {lang} in one request...")
        translated_text = translator.translate(batch_text)
        
        # Split by the translated delimiter. Note: Google Translate might add spaces around |||
        # Or it might translate the pipes. Let's hope it preserves '|||'
        translated_list = [x.strip() for x in translated_text.split('|||')]
        
        if len(translated_list) != len(msgids):
            print(f"Warning for {lang}: split length {len(translated_list)} != {len(msgids)}. Will try fallback char...")
            # Fallback for delimiter translation issues
            batch_text2 = "\n\n".join(msgids)
            translated_text2 = translator.translate(batch_text2)
            translated_list = [x.strip() for x in translated_text2.split('\n\n')]
        
        for i, entry in enumerate(untranslated):
            if i < len(translated_list):
                entry.msgstr = translated_list[i]
            else:
                entry.msgstr = entry.msgid
            
        po.save()
        print(f"Saved {lang}.")
        
    except Exception as e:
        print(f"Error translating {lang}: {e}")
        
    time.sleep(0.5)
