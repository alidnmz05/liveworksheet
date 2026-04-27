from django.db import models
from django.conf import settings
import uuid


class Workbook(models.Model):
    """Birden fazla çalışma kağıdını birleştiren dijital defter."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workbooks')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='workbook_covers/', blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Dijital Defter'
        verbose_name_plural = 'Dijital Defterler'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class WorkbookPage(models.Model):
    """Defterdeki bir çalışma kağıdı referansı."""
    workbook = models.ForeignKey(Workbook, on_delete=models.CASCADE, related_name='pages')
    worksheet = models.ForeignKey('worksheets.Worksheet', on_delete=models.CASCADE)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['order']
        unique_together = ('workbook', 'worksheet')

    def __str__(self):
        return f"{self.workbook.title} → {self.worksheet.title}"
