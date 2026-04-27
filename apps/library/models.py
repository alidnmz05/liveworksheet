from django.db import models
from django.conf import settings


class LibraryItem(models.Model):
    """Topluluk kütüphanesine eklenen çalışma kağıdı."""
    worksheet = models.OneToOneField('worksheets.Worksheet', on_delete=models.CASCADE,
                                      related_name='library_item')
    featured = models.BooleanField(default=False)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_items', blank=True)
    saved_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='saved_items', blank=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Kütüphane Öğesi'
        verbose_name_plural = 'Kütüphane Öğeleri'

    def __str__(self):
        return str(self.worksheet)

    @property
    def like_count(self):
        return self.likes.count()
