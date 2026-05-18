from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
import uuid
import json


class Subject(models.Model):
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, blank=True)

    class Meta:
        verbose_name = 'Ders'
        verbose_name_plural = 'Dersler'

    def __str__(self):
        return self.name


class Worksheet(models.Model):
    LEVEL_CHOICES = [
        ('anaokulu', _('Anaokulu')),
        ('ilkokul', _('İlkokul')),
        ('ortaokul', _('Ortaokul')),
        ('lise', _('Lise')),
        ('universite', _('Üniversite')),
        ('yetiskin', _('Yetişkin')),
    ]
    LANGUAGE_CHOICES = [
        ('tr', _('Türkçe')), ('en', _('İngilizce')), ('de', _('Almanca')),
        ('fr', _('Fransızca')), ('es', _('İspanyolca')), ('ar', _('Arapça')),
        ('pt', _('Portekizce')), ('ru', _('Rusça')), ('zh-hans', _('Çince')),
        ('it', _('İtalyanca')), ('ko', _('Korece')),
    ]
    GRADING_100 = '100'
    GRADING_10 = '10'
    GRADING_CHOICES = [
        (GRADING_100, _("100'lük Sistem (0–100 puan)")),
        (GRADING_10, _("10'luk Sistem (0–10 puan)")),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worksheets')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, blank=True)
    language = models.CharField(max_length=15, choices=LANGUAGE_CHOICES, default='tr')
    grading_system = models.CharField(
        max_length=3,
        choices=GRADING_CHOICES,
        default=GRADING_100,
        verbose_name='Puanlama Sistemi',
        help_text='Öğrenciye gösterilecek puan sistemi'
    )
    is_public = models.BooleanField(default=True)
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    tags = models.CharField(max_length=500, blank=True, help_text='Virgülle ayrılmış etiketler')
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Dummy translations for database objects (Subjects) so makemessages picks them up
    _DUMMY_SUBJECTS = [
        _('Matematik'), _('Türkçe'), _('İngilizce'), _('Tarih'), _('Coğrafya'),
        _('Fizik'), _('Kimya'), _('Biyoloji'), _('Fen Bilimleri'), _('Sosyal Bilgiler'),
        _('Hayat Bilgisi'), _('Din Kültürü'), _('Yabancı Dil'), _('Müzik'), _('Resim')
    ]

    class Meta:
        verbose_name = 'Çalışma Kağıdı'
        verbose_name_plural = 'Çalışma Kağıtları'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def tag_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]

    @property
    def total_questions_count(self):
        return Question.objects.filter(page__worksheet=self).exclude(
            question_type__in=['simple_text', 'play_mp3']
        ).count()

    @property
    def question_count(self):
        return self.total_questions_count


class WorksheetPage(models.Model):
    """Bir çalışma kağıdının bir sayfası (arka plan görseli + sorular)."""
    worksheet = models.ForeignKey(Worksheet, on_delete=models.CASCADE, related_name='pages')
    order = models.PositiveIntegerField(default=1)
    background_image = models.ImageField(upload_to='backgrounds/', blank=True, null=True)
    background_pdf = models.FileField(upload_to='pdfs/', blank=True, null=True)
    page_width = models.PositiveIntegerField(default=794)   # px (A4 @ 96dpi)
    page_height = models.PositiveIntegerField(default=1123)  # px
    # Ses ve metin okuma
    audio_file = models.FileField(upload_to='audio/', blank=True, null=True)
    audio_url = models.URLField(blank=True)
    text_to_speech_text = models.TextField(blank=True)
    text_to_speech_lang = models.CharField(max_length=5, default='tr')

    class Meta:
        ordering = ['order']
        verbose_name = 'Sayfa'
        verbose_name_plural = 'Sayfalar'

    def __str__(self):
        return f"{self.worksheet.title} - Sayfa {self.order}"


class MediaEmbed(models.Model):
    """Sayfaya gömülen video (YouTube/Vimeo)."""
    TYPE_YOUTUBE = 'youtube'
    TYPE_VIMEO = 'vimeo'
    TYPE_CHOICES = [(TYPE_YOUTUBE, 'YouTube'), (TYPE_VIMEO, 'Vimeo')]

    page = models.ForeignKey(WorksheetPage, on_delete=models.CASCADE, related_name='embeds')
    embed_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    video_url = models.URLField()
    video_id = models.CharField(max_length=50, blank=True)
    pos_x = models.FloatField(default=0)   # % cinsinden
    pos_y = models.FloatField(default=0)
    width = models.FloatField(default=40)  # %
    height = models.FloatField(default=25) # %

    def save(self, *args, **kwargs):
        if self.embed_type == self.TYPE_YOUTUBE and not self.video_id:
            import re
            m = re.search(r'(?:v=|youtu\.be/)([^&\n?#]+)', self.video_url)
            if m:
                self.video_id = m.group(1)
        super().save(*args, **kwargs)

    @property
    def embed_url(self):
        if self.embed_type == self.TYPE_YOUTUBE:
            return f'https://www.youtube.com/embed/{self.video_id}'
        return self.video_url


class Question(models.Model):
    TYPE_FILL_BLANK = 'fill_blank'
    TYPE_MULTIPLE_CHOICE = 'multiple_choice'
    TYPE_CHECKBOXES = 'checkboxes'
    TYPE_DROPDOWN = 'dropdown'
    TYPE_DRAG_DROP = 'drag_drop'
    TYPE_DRAG_WORD = 'drag_word'
    TYPE_DROP_ZONE = 'drop_zone'
    TYPE_MATCHING = 'matching'
    TYPE_SPEECH = 'speech'
    TYPE_OPEN_ANSWER = 'open_answer'
    TYPE_SIMPLE_TEXT = 'simple_text'
    TYPE_PLAY_MP3 = 'play_mp3'
    TYPE_WORD_CHOICE = 'word_choice'

    TYPE_CHOICES = [
        (TYPE_FILL_BLANK, 'Textfield'),
        (TYPE_MULTIPLE_CHOICE, 'Single Choice'),
        (TYPE_CHECKBOXES, 'Checkboxes'),
        (TYPE_DROPDOWN, 'Select'),
        (TYPE_DRAG_DROP, 'Drag & Drop (eski)'),
        (TYPE_DRAG_WORD, 'Drag Word'),
        (TYPE_DROP_ZONE, 'Drop Zone'),
        (TYPE_MATCHING, 'Join'),
        (TYPE_SPEECH, 'Speak'),
        (TYPE_OPEN_ANSWER, 'Open Answer'),
        (TYPE_SIMPLE_TEXT, 'Simple Text'),
        (TYPE_PLAY_MP3, 'Play MP3'),
        (TYPE_WORD_CHOICE, 'Kelime Seçimi (word1 / word2)'),
    ]

    page = models.ForeignKey(WorksheetPage, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    order = models.PositiveIntegerField(default=1)

    # Konumlandırma (% cinsinden, sayfaya göre)
    pos_x = models.FloatField(default=10)
    pos_y = models.FloatField(default=10)
    width = models.FloatField(default=15)
    height = models.FloatField(default=5)

    # Soru metni (opsiyonel, etiket olarak gösterilebilir)
    label = models.CharField(max_length=500, blank=True)

    # Doğru cevap (fill_blank, multiple_choice, dropdown için)
    correct_answer = models.TextField(blank=True)

    # Puan
    points = models.PositiveIntegerField(default=1, help_text='Bu soru kaç puan değerinde?')

    # Öğrenme Kazanımı & Yapay Zeka Etiketi
    learning_objective = models.CharField(
        max_length=500, blank=True,
        help_text='Yapay Zeka öneri motoru için öğrenme kazanımı/etiketi (Örn: "Kesirlerde Toplama", "Geçmiş Zaman Kişi Ekleri")'
    )

    # Stil
    font_size = models.PositiveIntegerField(default=14)
    bg_color = models.CharField(max_length=7, default='#ffffff')
    border_color = models.CharField(max_length=7, default='#cccccc')

    class Meta:
        ordering = ['order']
        verbose_name = 'Soru'
        verbose_name_plural = 'Sorular'

    def __str__(self):
        return f"{self.get_question_type_display()} - {self.page}"

    def get_correct_answer_text(self):
        """Soru tipine göre doğru cevabın okunabilir metnini döner."""
        if self.question_type == self.TYPE_FILL_BLANK:
            return self.correct_answer.replace('|', ' veya ')
        
        if self.question_type in (self.TYPE_MULTIPLE_CHOICE, self.TYPE_DROPDOWN, self.TYPE_CHECKBOXES):
            corrects = self.options.filter(is_correct=True).values_list('text', flat=True)
            return ", ".join(corrects)
            
        if self.question_type == self.TYPE_WORD_CHOICE:
            parts = [p.strip() for p in self.label.split('/')]
            try:
                idx = int(self.correct_answer) - 1
                if 0 <= idx < len(parts):
                    return parts[idx]
            except (ValueError, TypeError):
                pass
            return self.correct_answer

        if self.question_type == self.TYPE_MATCHING:
            pairs = self.matching_pairs.all()
            return "; ".join([f"{p.left_text} → {p.right_text}" for p in pairs])

        return self.correct_answer


class ChoiceOption(models.Model):
    """Çoktan seçmeli veya dropdown seçenekleri."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.text


class DragDropItem(models.Model):
    """Sürükle-bırak: sürüklenecek parça."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='drag_items')
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to='drag_items/', blank=True, null=True)
    correct_target_id = models.CharField(max_length=50, blank=True,
                                          help_text='Hangi hedef kutucuğa ait')
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']


class DragDropTarget(models.Model):
    """Sürükle-bırak: hedef kutu."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='drop_targets')
    target_id = models.CharField(max_length=50)
    label = models.CharField(max_length=255, blank=True)
    pos_x = models.FloatField(default=0)
    pos_y = models.FloatField(default=0)
    width = models.FloatField(default=10)
    height = models.FloatField(default=5)

    class Meta:
        pass


class MatchingPair(models.Model):
    """Eşleştirme sorusu çifti."""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='matching_pairs')
    left_text = models.CharField(max_length=255)
    right_text = models.CharField(max_length=255)
    left_image = models.ImageField(upload_to='matching/', blank=True, null=True)
    right_image = models.ImageField(upload_to='matching/', blank=True, null=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
