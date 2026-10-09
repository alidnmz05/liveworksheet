from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.workbooks.models import Workbook, WorkbookPage
from apps.worksheets.models import Worksheet

User = get_user_model()


class WorkbookModelAndViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Password123!'
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.worksheet = Worksheet.objects.create(
            author=self.teacher,
            title='Test Çalışma Kağıdı'
        )
        self.workbook = Workbook.objects.create(
            teacher=self.teacher,
            title='İlkokul Matematik Seti',
            description='Açıklama'
        )
        self.wb_page = WorkbookPage.objects.create(
            workbook=self.workbook,
            worksheet=self.worksheet,
            order=1
        )

    def test_workbook_model_str(self):
        self.assertEqual(str(self.workbook), 'İlkokul Matematik Seti')
        self.assertIn('İlkokul Matematik Seti', str(self.wb_page))

    def test_workbook_list_view(self):
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.get(reverse('workbook_list'))
        self.assertEqual(response.status_code, 200)

    def test_workbook_create_view_post(self):
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.post(reverse('workbook_create'), {
            'title': 'Yeni Fen Defteri',
            'description': 'Fen Bilgisi Etkinlikleri',
            'worksheet_ids': [str(self.worksheet.id)]
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Workbook.objects.filter(title='Yeni Fen Defteri').exists())

    def test_workbook_detail_view(self):
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.get(reverse('workbook_detail', kwargs={'pk': self.workbook.id}))
        self.assertEqual(response.status_code, 200)

    def test_workbook_delete(self):
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.post(reverse('workbook_delete', kwargs={'pk': self.workbook.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Workbook.objects.filter(id=self.workbook.id).exists())
