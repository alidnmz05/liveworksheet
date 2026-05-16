import os

replacements = {
    # workbooks/create.html
    'Yeni Dijital Defter': '{% trans "Yeni Dijital Defter" %}',
    'placeholder="Defter başlığı"': 'placeholder="{% trans \'Defter başlığı\' %}"',
    'Defter başlığı': '{% trans "Defter başlığı" %}',

    # accounts/classroom_list.html
    'Sınıflarım': '{% trans "Sınıflarım" %}',
    'Yeni Sınıf': '{% trans "Yeni Sınıf" %}',
    'placeholder="Sınıf kodu"': 'placeholder="{% trans \'Sınıf kodu\' %}"',
    '> Katıl<': '> {% trans "Katıl" %}<',
    'öğrenci</p>': '{% trans "öğrenci" %}</p>',
    'Henüz sınıfınız yok': '{% trans "Henüz sınıfınız yok" %}',
    'Henüz bir sınıfa katılmadınız': '{% trans "Henüz bir sınıfa katılmadınız" %}',
    'Öğretmeninizden sınıf kodunu alın ve yukarıya girin.': '{% trans "Öğretmeninizden sınıf kodunu alın ve yukarıya girin." %}',
    'Sınıf kodu': '{% trans "Sınıf kodu" %}',

    # workbooks/list.html
    'Henüz defter yok': '{% trans "Henüz defter yok" %}',
    'Henüz defteriniz yok': '{% trans "Henüz defteriniz yok" %}',
    'Defter Oluştur': '{% trans "Defter Oluştur" %}',
}

files = [
    'templates/workbooks/create.html',
    'templates/accounts/classroom_list.html',
    'templates/workbooks/list.html'
]

for file in files:
    full_path = '/Users/ismaildundar/Desktop/bitirmeProjesi/liveworksheet/' + file
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Sadece eksik {% trans %} taglarını değiştir (var olanları bozmamaya dikkat et)
        for k, v in replacements.items():
            if k in content and v not in content:
                content = content.replace(k, v)
                
        with open(full_path, 'w') as f:
            f.write(content)

print("Remaining templates localized.")
