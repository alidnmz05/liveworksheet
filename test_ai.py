import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.submissions.ai_engine import evaluate_open_answer
print(evaluate_open_answer("dalgalar halinde", "dalgalar şeklinde yayılır"))
