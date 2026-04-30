from django.db import models
from django.conf import settings


class Submission(models.Model):
    """Öğrencinin bir çalışma kağıdına verdiği yanıtların tamamı."""
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    worksheet = models.ForeignKey('worksheets.Worksheet', on_delete=models.CASCADE,
                                   related_name='submissions', null=True, blank=True)
    assignment = models.ForeignKey('assignments.Assignment', on_delete=models.SET_NULL,
                                    null=True, blank=True, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)
    score = models.FloatField(null=True, blank=True)          # 0-100
    total_questions = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    is_graded = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Gönderim'
        verbose_name_plural = 'Gönderimler'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.student.email} – {self.worksheet}"

    def calculate_score(self):
        # Her soru kendi points değeriyle ağırlıklandırılır.
        # Eşleştirme/drag-drop gibi çok öğeli soru tipleri için
        # kısmi puan: (correct_items / total_items) * points
        total_pts = 0
        earned_pts = 0.0
        for a in self.answers.all():
            pts = a.question.points if a.question.points else 1
            if a.total_items > 0:
                total_pts += pts
                earned_pts += (a.correct_items / a.total_items) * pts
        self.total_questions = total_pts
        self.correct_count = int(round(earned_pts))
        self.score = round((earned_pts / total_pts) * 100, 1) if total_pts > 0 else 0
        self.is_graded = True
        self.save()
        return self.score


class Answer(models.Model):
    """Tek bir soruya verilen yanıt."""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('worksheets.Question', on_delete=models.CASCADE)
    given_answer = models.TextField(blank=True)  # JSON string for complex types
    is_correct = models.BooleanField(null=True)
    # Liveworksheets.com gibi eşleştirme/sürükle-bırak için kısmi puan desteği
    correct_items = models.PositiveIntegerField(default=0)
    total_items = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"Q{self.question_id}: {self.given_answer[:30]}"

    def check_answer(self):
        q = self.question
        from apps.worksheets.models import Question as Q
        if q.question_type == Q.TYPE_FILL_BLANK:
            given = self.given_answer.strip().lower()
            accepted = [a.strip().lower() for a in q.correct_answer.split('|') if a.strip()]
            self.is_correct = given in accepted if accepted else (given == '')
            self.total_items = 1
            self.correct_items = 1 if self.is_correct else 0
        elif q.question_type in (Q.TYPE_MULTIPLE_CHOICE, Q.TYPE_DROPDOWN):
            correct_opts = set(
                q.options.filter(is_correct=True).values_list('text', flat=True)
            )
            self.is_correct = self.given_answer.strip() in correct_opts
            self.total_items = 1
            self.correct_items = 1 if self.is_correct else 0
        elif q.question_type == Q.TYPE_DRAG_DROP:
            import json
            try:
                given = json.loads(self.given_answer)
                self.total_items = len(given)
                correct_count = sum(
                    1 for item in given
                    if item.get('target') == item.get('expected')
                )
                self.correct_items = correct_count
                self.is_correct = correct_count == self.total_items
            except (json.JSONDecodeError, AttributeError):
                self.is_correct = False
                self.total_items = 0
                self.correct_items = 0
        elif q.question_type == Q.TYPE_MATCHING:
            import json
            try:
                given = json.loads(self.given_answer)
                pairs = {p.left_text: p.right_text for p in q.matching_pairs.all()}
                self.total_items = len(pairs)
                correct_count = sum(
                    1 for k, v in pairs.items() if given.get(k) == v
                )
                self.correct_items = correct_count
                self.is_correct = correct_count == self.total_items
            except (json.JSONDecodeError, AttributeError):
                self.is_correct = False
                self.total_items = 0
                self.correct_items = 0
        elif q.question_type == Q.TYPE_CHECKBOXES:
            import json
            try:
                given = set(json.loads(self.given_answer))
                correct = set(
                    q.options.filter(is_correct=True).values_list('text', flat=True)
                )
                self.is_correct = given == correct
            except (json.JSONDecodeError, AttributeError, TypeError):
                self.is_correct = False
            self.total_items = 1
            self.correct_items = 1 if self.is_correct else 0
        elif q.question_type in (Q.TYPE_SPEECH, Q.TYPE_OPEN_ANSWER,
                                  Q.TYPE_PLAY_MP3, Q.TYPE_SIMPLE_TEXT):
            # Manuel değerlendirme veya cevap gerekmez — puandan hariç
            self.is_correct = None
            self.total_items = 0
            self.correct_items = 0
        self.save()
        return self.is_correct
