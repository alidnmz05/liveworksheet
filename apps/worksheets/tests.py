from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.worksheets.models import Subject, Worksheet, WorksheetPage, Question, ChoiceOption

User = get_user_model()


class WorksheetModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='author@example.com',
            email='author@example.com',
            password='Password123!',
            role=User.ROLE_TEACHER
        )
        self.subject = Subject.objects.create(name='Matematik')
        self.worksheet = Worksheet.objects.create(
            author=self.user,
            title='Kesirler Çalışması',
            subject=self.subject,
            tags='matematik, kesirler, 5.sınıf'
        )

    def test_worksheet_properties(self):
        self.assertEqual(str(self.worksheet), 'Kesirler Çalışması')
        self.assertEqual(self.worksheet.tag_list, ['matematik', 'kesirler', '5.sınıf'])
        self.assertEqual(self.worksheet.total_questions_count, 0)

    def test_page_and_question_relations(self):
        page = WorksheetPage.objects.create(worksheet=self.worksheet, order=1)
        question = Question.objects.create(
            page=page,
            question_type=Question.TYPE_MULTIPLE_CHOICE,
            label='1/2 hangisine eşittir?',
            pos_x=10,
            pos_y=20,
            width=200,
            height=100
        )
        ChoiceOption.objects.create(question=question, text='%50', is_correct=True)
        ChoiceOption.objects.create(question=question, text='%25', is_correct=False)

        self.assertEqual(self.worksheet.total_questions_count, 1)
        self.assertEqual(question.options.count(), 2)
        self.assertEqual(question.get_correct_answer_text(), '%50')


class WorksheetViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Password123!'
        self.author = User.objects.create_user(
            username='author@example.com',
            email='author@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.other_user = User.objects.create_user(
            username='other@example.com',
            email='other@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.subject = Subject.objects.create(name='Fen Bilimleri')
        self.worksheet = Worksheet.objects.create(
            author=self.author,
            title='Hücre Bölünmesi',
            subject=self.subject,
            is_public=True
        )

    def test_worksheet_list_view(self):
        self.client.login(email='author@example.com', password=self.password)
        response = self.client.get(reverse('worksheet_list'))
        self.assertEqual(response.status_code, 200)

    def test_worksheet_create_view_post(self):
        self.client.login(email='author@example.com', password=self.password)
        response = self.client.post(reverse('worksheet_create'), {
            'title': 'Yeni Fizik Kağıdı',
            'description': 'Açıklama',
            'subject': self.subject.id,
            'level': 'ortaokul',
            'language': 'tr',
            'grading_system': '100',
            'is_public': True
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Worksheet.objects.filter(title='Yeni Fizik Kağıdı').exists())

    def test_worksheet_detail_and_editor_access(self):
        # Public worksheet detail accessible by anyone
        response = self.client.get(reverse('worksheet_detail', kwargs={'pk': self.worksheet.id}))
        self.assertEqual(response.status_code, 200)

        # Editor accessible by author
        self.client.login(email='author@example.com', password=self.password)
        editor_resp = self.client.get(reverse('worksheet_editor', kwargs={'pk': self.worksheet.id}))
        self.assertEqual(editor_resp.status_code, 200)

        # Editor restricted for non-author
        self.client.login(email='other@example.com', password=self.password)
        other_resp = self.client.get(reverse('worksheet_editor', kwargs={'pk': self.worksheet.id}))
        self.assertNotEqual(other_resp.status_code, 200)

    def test_worksheet_delete(self):
        self.client.login(email='author@example.com', password=self.password)
        response = self.client.post(reverse('worksheet_delete', kwargs={'pk': self.worksheet.id}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Worksheet.objects.filter(id=self.worksheet.id).exists())
