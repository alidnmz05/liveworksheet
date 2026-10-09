import os
import polib

base_dir = '/Users/ismaildundar/Desktop/bitirmeProjesi/liveworksheet/locale'
lang_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

for lang in lang_dirs:
    po_path = os.path.join(base_dir, lang, 'LC_MESSAGES', 'django.po')
    if os.path.exists(po_path):
        po = polib.pofile(po_path)
        count = 0
        for entry in po:
            if entry.fuzzy:
                entry.fuzzy = False
                count += 1
        po.save()
        print(f"Removed fuzzy flag from {count} entries in {lang}.")
