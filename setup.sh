#!/usr/bin/env bash
# Setup script for LiveWorksheet

echo "=== LiveWorksheet Kurulum ==="

# Create virtual environment
python -m venv venv
source venv/Scripts/activate 2>/dev/null || source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env
echo ">>> .env dosyası oluşturuldu. SECRET_KEY'i değiştirmeyi unutmayın!"

# Migrations
python manage.py migrate

# Load fixtures
python manage.py loaddata apps/worksheets/fixtures/subjects.json

# Collect static
python manage.py collectstatic --noinput

# Create superuser (interactive)
echo ">>> Yönetici hesabı oluşturun:"
python manage.py createsuperuser

echo "=== Kurulum tamamlandı! ==="
echo "Başlatmak için: python manage.py runserver"
