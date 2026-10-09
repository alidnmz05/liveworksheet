from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.library.models import LibraryItem
from apps.worksheets.models import Worksheet, Subject

User = get_user_model()


class LibraryModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Password123!'
        self.user = User.objects.create_user(
            username='user@example.com',
            email='user@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.subject = Subject.objects.create(name='Tarih')
        self.worksheet = Worksheet.objects.create(
            author=self.user,
            title='Osmanlı Tarihi Testi',
            subject=self.subject,
            is_public=True
        )
        self.lib_item, _ = LibraryItem.objects.get_or_create(worksheet=self.worksheet)

    def test_library_item_str_and_like_count(self):
        self.assertEqual(str(self.lib_item), 'Osmanlı Tarihi Testi')
        self.assertEqual(self.lib_item.like_count, 0)

    def test_library_index_view(self):
        response = self.client.get(reverse('library_index'))
        self.assertEqual(response.status_code, 200)

        # Search query filter
        response_q = self.client.get(reverse('library_index') + '?q=Osmanlı')
        self.assertEqual(response_q.status_code, 200)

    def test_library_like_and_save(self):
        self.client.login(email='user@example.com', password=self.password)

        # Like
        response_like = self.client.post(reverse('library_like', kwargs={'pk': self.lib_item.pk}))
        self.assertEqual(response_like.status_code, 200)
        self.assertEqual(self.lib_item.like_count, 1)

        # Save / Bookmark
        response_save = self.client.post(reverse('library_save', kwargs={'pk': self.lib_item.pk}))
        self.assertEqual(response_save.status_code, 200)
        self.assertTrue(self.lib_item.saved_by.filter(id=self.user.id).exists())
