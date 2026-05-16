import os
import re

files_to_process = [
    'templates/worksheets/create.html',
    'templates/worksheets/detail.html',
    'templates/home.html',
    'templates/accounts/profile.html',
    'templates/accounts/classroom_list.html',
    'templates/accounts/classroom_detail.html',
    'templates/accounts/classroom_form.html',
    'templates/workbooks/list.html',
    'templates/workbooks/create.html',
    'templates/workbooks/detail.html',
    'templates/assignments/create.html',
    'templates/assignments/detail.html',
    'templates/submissions/detail.html',
    'templates/worksheets/editor.html'
]

replacements = {
    # worksheets/create.html
    '>Geri<': '>{% trans "Geri" %}<',
    'Yeni Çalışma Kağıdı': '{% trans "Yeni Çalışma Kağıdı" %}',
    'PDF Dosyası': '{% trans "PDF Dosyası" %}',
    '(opsiyonel — her sayfa otomatik oluşturulur)': '{% trans "(opsiyonel — her sayfa otomatik oluşturulur)" %}',
    'PDF dosyası seçin veya buraya sürükleyin': '{% trans "PDF dosyası seçin veya buraya sürükleyin" %}',
    'Maks. 50 MB': '{% trans "Maks. 50 MB" %}',
    '> Kaldır<': '> {% trans "Kaldır" %}<',
    '>veya bilgileri doldurun<': '>{% trans "veya bilgileri doldurun" %}<',
    '>Başlık': '>{% trans "Başlık" %}',
    'placeholder="Örn: 2. Sınıf Toplama İşlemi"': 'placeholder="{% trans \'Örn: 2. Sınıf Toplama İşlemi\' %}"',
    '>Açıklama<': '>{% trans "Açıklama" %}<',
    'placeholder="Kağıt hakkında kısa bir açıklama"': 'placeholder="{% trans \'Kağıt hakkında kısa bir açıklama\' %}"',
    '>Ders<': '>{% trans "Ders" %}<',
    '>Seçin...<': '>{% trans "Seçin..." %}<',
    '>Seviye<': '>{% trans "Seviye" %}<',
    '>Dil<': '>{% trans "Dil" %}<',
    '>Etiketler<': '>{% trans "Etiketler" %}<',
    'placeholder="matematik, toplama"': 'placeholder="{% trans \'matematik, toplama\' %}"',
    '>Puanlama Sistemi': '>{% trans "Puanlama Sistemi" %}',
    '(öğrenciye gösterilecek puan)': '{% trans "(öğrenciye gösterilecek puan)" %}',
    "100'lük Sistem": "{% trans \"100'lük Sistem\" %}",
    "Öğrenciye 0–100 arası puan gösterilir": "{% trans 'Öğrenciye 0–100 arası puan gösterilir' %}",
    '>Seçili<': '>{% trans "Seçili" %}<',
    "10'luk Sistem": "{% trans \"10'luk Sistem\" %}",
    "Öğrenciye 0–10 arası puan gösterilir": "{% trans 'Öğrenciye 0–10 arası puan gösterilir' %}",
    "Herkese açık (kütüphaneye eklenebilir)": "{% trans 'Herkese açık (kütüphaneye eklenebilir)' %}",
    '>Oluştur ve Düzenle<': '>{% trans "Oluştur ve Düzenle" %}<',
    '>İptal<': '>{% trans "İptal" %}<',
    'PDF yüklendi — sayfa sayısı işlem sırasında belirlenir.': "{% trans 'PDF yüklendi — sayfa sayısı işlem sırasında belirlenir.' %}",
    'PDF İşle ve Oluştur': "{% trans 'PDF İşle ve Oluştur' %}",
    'PDF işleniyor, lütfen bekleyin...': "{% trans 'PDF işleniyor, lütfen bekleyin...' %}",

    # home.html
    "Etkileşimli <span class=\"text-indigo-600\">Çalışma Kağıtları</span> Oluşturun": "{% trans 'Etkileşimli' %} <span class=\"text-indigo-600\">{% trans 'Çalışma Kağıtları' %}</span> {% trans 'Oluşturun' %}",
    "PDF ve görsellerinizi; sürükle-bırak, çoktan seçmeli, sesli yanıt gibi interaktif sorularla dönüştürün.\n        Öğrencilerinizi takip edin, anında puan verin.": "{% trans 'PDF ve görsellerinizi; sürükle-bırak, çoktan seçmeli, sesli yanıt gibi interaktif sorularla dönüştürün. Öğrencilerinizi takip edin, anında puan verin.' %}",
    "Ücretsiz Başla": "{% trans 'Ücretsiz Başla' %}",
    "Kütüphaneye Göz At": "{% trans 'Kütüphaneye Göz At' %}",

    # accounts/profile.html
    ">Profilim<": ">{% trans 'Profilim' %}<",
    ">Profil fotoğrafı<": ">{% trans 'Profil fotoğrafı' %}<",
    ">Profil Fotoğrafı<": ">{% trans 'Profil Fotoğrafı' %}<",
    ">Ad<": ">{% trans 'Ad' %}<",
    ">Soyad<": ">{% trans 'Soyad' %}<",
    ">Okul/Kurum<": ">{% trans 'Okul/Kurum' %}<",
    ">Ülke<": ">{% trans 'Ülke' %}<",
    ">Hakkında<": ">{% trans 'Hakkında' %}<",
    ">Güncelle<": ">{% trans 'Güncelle' %}<",
    
    # worksheets/detail.html
    ">Çöz<": ">{% trans 'Çöz' %}<",
    ">Düzenle<": ">{% trans 'Düzenle' %}<",
    ">Kütüphaneye Ekle<": ">{% trans 'Kütüphaneye Ekle' %}<",
    
    # workbooks
    "Defterlerim": "{% trans 'Defterlerim' %}",
    "Yeni Defter": "{% trans 'Yeni Defter' %}",
    "Henüz defteriniz yok": "{% trans 'Henüz defteriniz yok' %}",
    "Çalışma kağıtlarınızı gruplamak için defterler oluşturun.": "{% trans 'Çalışma kağıtlarınızı gruplamak için defterler oluşturun.' %}",
    ">Defter Adı<": ">{% trans 'Defter Adı' %}<",
    ">Oluştur<": ">{% trans 'Oluştur' %}<",
    ">Kaydet<": ">{% trans 'Kaydet' %}<",
    
    # classroom
    "Sınıf Oluştur": "{% trans 'Sınıf Oluştur' %}",
    "Sınıf Adı": "{% trans 'Sınıf Adı' %}",
    "Sınıf Kodu": "{% trans 'Sınıf Kodu' %}",
    "Öğrenciler": "{% trans 'Öğrenciler' %}",
    
    # assignments
    "Ödev Ver": "{% trans 'Ödev Ver' %}",
    "Ödev Adı": "{% trans 'Ödev Adı' %}",
    "Başlangıç Tarihi": "{% trans 'Başlangıç Tarihi' %}",
    "Bitiş Tarihi": "{% trans 'Bitiş Tarihi' %}",
    
    # common
    ">Sil<": ">{% trans 'Sil' %}<",
    ">Vazgeç<": ">{% trans 'Vazgeç' %}<",
    ">Emin misiniz?<": ">{% trans 'Emin misiniz?' %}<",
}

for path in files_to_process:
    full_path = '/Users/ismaildundar/Desktop/bitirmeProjesi/liveworksheet/' + path
    if not os.path.exists(full_path):
        continue
        
    with open(full_path, 'r') as f:
        content = f.read()
        
    if '{% load i18n %}' not in content:
        content = content.replace("{% extends 'base.html' %}", "{% extends 'base.html' %}\n{% load i18n %}")
        content = content.replace('{% extends "base.html" %}', '{% extends "base.html" %}\n{% load i18n %}')
        
    for k, v in replacements.items():
        content = content.replace(k, v)
        
    with open(full_path, 'w') as f:
        f.write(content)
        
print("Templates localized.")
