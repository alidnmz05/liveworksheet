import os
import polib
from deep_translator import GoogleTranslator
import time

# We only focus on English translation as requested, prioritizing TR -> EN
lang_map = {
    'en': 'en'
}

base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locale')

for lang, g_lang in lang_map.items():
    po_file_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'django.po')
    mo_file_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'django.mo')
    
    if not os.path.exists(po_file_path):
        print(f"PO file not found at: {po_file_path}")
        continue
    
    print(f"Processing {lang}...")
    po = polib.pofile(po_file_path)
    translator = GoogleTranslator(source='tr', target=g_lang)
    
    # We want to translate untranslated entries
    untranslated = po.untranslated_entries()
    if not untranslated:
        print(f"No untranslated entries for {lang}.")
        # Compile existing translation just in case
        po.save_as_mofile(mo_file_path)
        print(f"Compiled existing {lang} catalog.")
        continue

    print(f"Found {len(untranslated)} untranslated entries.")
    
    # Process in chunks of 30 to avoid API limitations/errors
    chunk_size = 30
    for idx in range(0, len(untranslated), chunk_size):
        chunk = untranslated[idx:idx+chunk_size]
        msgids = [entry.msgid.replace("\\'", "'") for entry in chunk]
        batch_text = " ||| ".join(msgids)
        
        try:
            print(f"Translating chunk {idx//chunk_size + 1}... ({len(chunk)} strings)")
            translated_text = translator.translate(batch_text)
            
            # Split and cleanup
            translated_list = [x.strip() for x in translated_text.split('|||')]
            
            if len(translated_list) != len(msgids):
                # Fallback if delimiter translated/modified
                print(f"Warning: split length mismatch ({len(translated_list)} vs {len(msgids)}). Retrying individual translations...")
                for item in chunk:
                    item.msgstr = translator.translate(item.msgid)
            else:
                for i, entry in enumerate(chunk):
                    entry.msgstr = translated_list[i]
            
            po.save()
            print("Chunk saved successfully.")
        except Exception as e:
            print(f"Error during chunk translation: {e}")
            # Fallback to individual translation for the chunk
            for item in chunk:
                try:
                    item.msgstr = translator.translate(item.msgid)
                except Exception:
                    item.msgstr = item.msgid
            po.save()
        
        time.sleep(0.5)

    # Save compiled catalog (.mo)
    po.save_as_mofile(mo_file_path)
    print(f"Successfully compiled translation file to: {mo_file_path}")
