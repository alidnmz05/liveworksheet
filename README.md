# LiveWorksheet

Django ile geliştirilmiş etkileşimli çalışma kağıdı platformu (öğretmen / öğrenci rolleri, çalışma kağıdı editörü, ödevler, kütüphane, çalışma kitapları).

## Gereksinimler

- Python 3.12
- Git

## Kurulum

```bash
git clone https://github.com/alidnmz05/liveworksheet.git
cd liveworksheet

python -m venv venv
# Windows (PowerShell):  venv\Scripts\Activate.ps1
# Linux / macOS / Git Bash:  source venv/bin/activate   (Git Bash'te: source venv/Scripts/activate)

pip install -r requirements.txt

# Ortam değişkenleri
cp .env.example .env        # Windows: copy .env.example .env
```

## Veritabanı (örnek veri ile)

Projede SQLite kullanılır. Hazır örnek veritabanını kopyalayarak çalışma kağıtları ve sorularla birlikte başlayabilirsin:

```bash
cp sample_data/db.sqlite3 db.sqlite3     # Windows: copy sample_data\db.sqlite3 db.sqlite3
python manage.py migrate                 # şema güncel değilse tamamlar
```

Örnek veritabanındaki kullanıcılarla giriş yapamazsan, kendi hesabını oluşturmak için
sitedeki kayıt sayfasını ya da `python manage.py createsuperuser` komutunu kullan.

Boş veritabanıyla başlamak istersen:

```bash
python manage.py migrate
python manage.py loaddata apps/worksheets/fixtures/subjects.json
python manage.py createsuperuser
```

## Çalıştırma

```bash
python manage.py runserver
```

Tarayıcıdan: http://127.0.0.1:8000/

## Testler

```bash
python manage.py test
```

## Notlar

- `db.sqlite3`, `media/` ve `.env` git'e dahil değildir; her geliştirici kendi kopyasını kullanır.
- Yüklenen görseller (`media/`) örnek veritabanıyla gelmez, bu yüzden bazı çalışma kağıtlarında görseller eksik görünebilir.
