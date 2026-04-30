"""
python manage.py create_demo --user <email>

Tüm bileşen türlerini içeren "İngilizce Demo Dersi" çalışma kağıdı oluşturur.
"""
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Tüm bileşenleri içeren demo çalışma kağıdı oluşturur.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, required=True,
                            help='Çalışma kağıdını oluşturacak kullanıcının e-posta adresi')

    def handle(self, *args, **options):
        from apps.worksheets.models import (
            Worksheet, WorksheetPage, Question,
            ChoiceOption, DragDropItem, MatchingPair
        )

        email = options['user']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f'"{email}" e-postasına sahip kullanıcı bulunamadı.')

        # ── Çalışma kağıdı ──────────────────────────────────────────
        ws = Worksheet.objects.create(
            author=user,
            title='🧩 Demo: Tüm Bileşenler',
            description='Editördeki her bileşen türünü gösteren örnek ders.',
            language='en',
            is_public=False,
        )

        # ── Sayfa 1 ─────────────────────────────────────────────────
        page = WorksheetPage.objects.create(
            worksheet=ws, order=1, page_width=794, page_height=1123
        )

        order = 0

        def q(qtype, label, correct='', x=5, y=None, w=0, h=0, pts=1):
            nonlocal order
            order += 1
            return Question.objects.create(
                page=page, question_type=qtype, label=label,
                correct_answer=correct,
                pos_x=x, pos_y=y if y is not None else order * 8,
                width=w, height=h, points=pts,
                font_size=14, bg_color='#ffffff', border_color='#d1d5db',
            )

        # 1. Simple Text — başlık
        q('simple_text', '🇬🇧  English Review — Unit 5', x=5, y=2)

        # 2. Play MP3 — dinleme parçası
        mp3_q = q('play_mp3', 'Listen to the dialogue', x=5, y=10)
        mp3_q.correct_answer = 'https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3'
        mp3_q.save()

        # 3. Fill Blank — boşluk doldurma
        q('fill_blank', 'The capital of France is ___.',
          correct='Paris', x=5, y=18, pts=2)

        # 4. Fill Blank — çoklu doğru cevap
        q('fill_blank', 'Water boils at ___ °C.',
          correct='100|one hundred', x=5, y=26, pts=2)

        # 5. Single Choice
        mc = q('multiple_choice', 'Which is a mammal?', x=5, y=34, pts=3)
        for i, (text, correct) in enumerate([
            ('Salmon', False), ('Eagle', False), ('Dolphin', True), ('Crocodile', False)
        ]):
            ChoiceOption.objects.create(question=mc, text=text, is_correct=correct, order=i+1)

        # 6. Checkboxes — birden fazla doğru
        cb = q('checkboxes', 'Select all prime numbers:', x=5, y=48, pts=4)
        for i, (text, correct) in enumerate([
            ('4', False), ('7', True), ('9', False), ('11', True), ('13', True)
        ]):
            ChoiceOption.objects.create(question=cb, text=text, is_correct=correct, order=i+1)

        # 7. Select / Dropdown
        dd = q('dropdown', 'Choose the correct article:', x=5, y=62, pts=2)
        for i, (text, correct) in enumerate([
            ('a', False), ('an', True), ('the', False), ('—', False)
        ]):
            ChoiceOption.objects.create(question=dd, text=text, is_correct=correct, order=i+1)

        # 8. Drag & Drop
        dnd = q('drag_drop', 'Drag each word to the correct category:', x=5, y=72, pts=5)
        items = [
            ('Apple', 'fruit'), ('Carrot', 'vegetable'), ('Banana', 'fruit'),
            ('Broccoli', 'vegetable'), ('Mango', 'fruit'),
        ]
        for i, (text, target) in enumerate(items):
            DragDropItem.objects.create(question=dnd, text=text, correct_target_id=target, order=i+1)

        # 9. Matching / Join
        match = q('matching', 'Match the countries with their capitals:', x=5, y=84, pts=5)
        pairs = [
            ('Germany', 'Berlin'), ('Japan', 'Tokyo'),
            ('Brazil', 'Brasília'), ('Australia', 'Canberra'),
        ]
        for i, (left, right) in enumerate(pairs):
            MatchingPair.objects.create(question=match, left_text=left, right_text=right, order=i+1)

        # 10. Open Answer
        q('open_answer', 'Describe your favourite season in 2-3 sentences.',
          correct='', x=5, y=94, pts=10)

        # 11. Speak
        q('speech', 'Read the following sentence aloud: "The quick brown fox jumps over the lazy dog."',
          x=55, y=18)

        self.stdout.write(self.style.SUCCESS(
            f'\n✅  Demo çalışma kağıdı oluşturuldu!\n'
            f'   Başlık : {ws.title}\n'
            f'   UUID   : {ws.pk}\n'
            f'   URL    : http://127.0.0.1:8000/worksheets/{ws.pk}/editor/\n'
            f'   Sayfa  : 1  |  Bileşen sayısı: {order}\n'
        ))
