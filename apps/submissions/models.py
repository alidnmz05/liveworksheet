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
        answers = self.answers.all()
        total = answers.count()
        correct = answers.filter(is_correct=True).count()
        self.total_questions = total
        self.correct_count = correct
        self.score = round((correct / total) * 100, 1) if total > 0 else 0
        self.is_graded = True
        self.save()
        return self.score


class Answer(models.Model):
    """Tek bir soruya verilen yanıt."""
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey('worksheets.Question', on_delete=models.CASCADE)
    given_answer = models.TextField(blank=True)  # JSON string for complex types
    is_correct = models.BooleanField(null=True)

    class Meta:
        unique_together = ('submission', 'question')

    def __str__(self):
        return f"Q{self.question_id}: {self.given_answer[:30]}"

    def check_answer(self):
        q = self.question
        from apps.worksheets.models import Question as Q
        if q.question_type == Q.TYPE_FILL_BLANK:
            self.is_correct = (
                self.given_answer.strip().lower() == q.correct_answer.strip().lower()
            )
        elif q.question_type in (Q.TYPE_MULTIPLE_CHOICE, Q.TYPE_DROPDOWN):
            correct_opts = set(
                q.options.filter(is_correct=True).values_list('text', flat=True)
            )
            self.is_correct = self.given_answer.strip() in correct_opts
        elif q.question_type == Q.TYPE_DRAG_DROP:
            import json
            try:
                given = json.loads(self.given_answer)
                all_correct = all(
                    item.get('target') == item.get('expected')
                    for item in given
                )
                self.is_correct = all_correct
            except (json.JSONDecodeError, AttributeError):
                self.is_correct = False
        elif q.question_type == Q.TYPE_MATCHING:
            import json
            try:
                given = json.loads(self.given_answer)
                pairs = {p.left_text: p.right_text for p in q.matching_pairs.all()}
                self.is_correct = all(
                    given.get(k) == v for k, v in pairs.items()
                )
            except (json.JSONDecodeError, AttributeError):
                self.is_correct = False
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
        elif q.question_type in (Q.TYPE_SPEECH, Q.TYPE_OPEN_ANSWER,
                                  Q.TYPE_PLAY_MP3, Q.TYPE_SIMPLE_TEXT):
            # Manuel değerlendirme veya cevap gerekmez
            self.is_correct = None
        self.save()
        return self.is_correct
