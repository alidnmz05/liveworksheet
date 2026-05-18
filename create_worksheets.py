import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.worksheets.models import Worksheet, WorksheetPage, Question, Subject

User = get_user_model()
email = "ogretmen@gmail.com"
password = "123456Aa*"

# Try to get or create the user, handling fields properly
try:
    user = User.objects.get(email=email)
except User.DoesNotExist:
    # Some custom user models don't have username
    user = User(email=email)
    user.set_password(password)
    user.save()

# In case it has username
if hasattr(user, 'username') and not user.username:
    user.username = "ogretmen"
    user.save()
    
# Make sure password is set correctly just in case
user.set_password(password)
user.save()

print(f"User {email} ready.")

# Get or create subject
subject, _ = Subject.objects.get_or_create(name="Türkçe")

titles = [
    "Okuma Anlama ve Yorumlama Etkinliği - 1",
    "Hikaye Tamamlama Çalışması",
    "Duygu ve Düşünce İfade Etme Alıştırması",
    "Görsel Yorumlama ve Metin Yazma",
    "Atasözleri ve Deyimler Yorumlama"
]

descriptions = [
    "Verilen metni okuyup ilgili açık uçlu soruları cevaplayınız.",
    "Yarım bırakılmış hikayeyi hayal gücünüzü kullanarak tamamlayınız.",
    "Belirtilen konularda kişisel görüşlerinizi ve düşüncelerinizi detaylı bir şekilde yazınız.",
    "Farklı konular üzerine kendi düşüncelerinizi ifade edebileceğiniz yazma çalışmaları.",
    "Verilen atasözü ve deyimlerin ne anlama geldiğini kendi cümlelerinizle açıklayınız."
]

for i in range(5):
    worksheet = Worksheet.objects.create(
        author=user,
        title=titles[i],
        description=descriptions[i],
        subject=subject,
        level='ortaokul',
        language='tr',
        is_public=True,
        tags='ortaokul,açıkuçlu,türkçe'
    )
    
    # Create a page
    page = WorksheetPage.objects.create(worksheet=worksheet, order=1)
    
    # Create an open ended question
    Question.objects.create(
        page=page,
        question_type=Question.TYPE_OPEN_ANSWER,
        order=1,
        pos_x=10,
        pos_y=20,
        width=80,
        height=30,
        label=f"Soru 1: Bu çalışma kağıdı ile ilgili düşüncelerinizi detaylıca açıklayınız."
    )
    
    # Create another open ended question
    Question.objects.create(
        page=page,
        question_type=Question.TYPE_OPEN_ANSWER,
        order=2,
        pos_x=10,
        pos_y=60,
        width=80,
        height=30,
        label=f"Soru 2: Konuyu kendi cümlelerinizle özetleyiniz."
    )
    
    print(f"Created worksheet: {worksheet.title}")

print("Done.")