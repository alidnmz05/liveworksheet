from django.db import models
from django.conf import settings
from django.utils import timezone


class Assignment(models.Model):
    """Öğretmenin sınıf(lar)a atadığı ödev."""
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignments_created')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    worksheet = models.ForeignKey('worksheets.Worksheet', on_delete=models.SET_NULL,
                                   null=True, blank=True, related_name='assignments')
    workbook = models.ForeignKey('workbooks.Workbook', on_delete=models.SET_NULL,
                                  null=True, blank=True, related_name='assignments')
    classrooms = models.ManyToManyField('accounts.Classroom', related_name='assignments', blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    allow_multiple_attempts = models.BooleanField(default=False)
    show_answers = models.BooleanField(default=True, help_text='Bitişte doğru cevapları göster')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Ödev'
        verbose_name_plural = 'Ödevler'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def is_overdue(self):
        if self.due_date:
            return timezone.now() > self.due_date
        return False

    def clean(self):
        from django.core.exceptions import ValidationError
        if not self.worksheet and not self.workbook:
            raise ValidationError('Çalışma kağıdı veya defter seçilmelidir.')
