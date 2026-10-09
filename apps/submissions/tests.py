from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch
from django.contrib.auth import get_user_model
from apps.worksheets.models import Worksheet, WorksheetPage, Question, ChoiceOption
from apps.submissions.models import Submission, Answer

User = get_user_model()


class SubmissionModelAndAITest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='Password123!',
            role=User.ROLE_TEACHER
        )
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='Password123!',
            role=User.ROLE_STUDENT
        )
        self.worksheet = Worksheet.objects.create(
            author=self.teacher,
            title='Biyoloji Testi'
        )
        self.page = WorksheetPage.objects.create(worksheet=self.worksheet, order=1)
        self.q1 = Question.objects.create(
            page=self.page,
            question_type=Question.TYPE_FILL_BLANK,
            correct_answer='Ankara|İstanbul',
            points=10
        )
        self.q2 = Question.objects.create(
            page=self.page,
            question_type=Question.TYPE_MULTIPLE_CHOICE,
            points=10
        )
        self.opt1 = ChoiceOption.objects.create(question=self.q2, text='A', is_correct=True)
        self.opt2 = ChoiceOption.objects.create(question=self.q2, text='B', is_correct=False)

    def test_submission_calculate_score(self):
        submission = Submission.objects.create(
            student=self.student,
            worksheet=self.worksheet
        )
        ans1 = Answer.objects.create(
            submission=submission,
            question=self.q1,
            given_answer='ankara'
        )
        ans1.check_answer()

        ans2 = Answer.objects.create(
            submission=submission,
            question=self.q2,
            given_answer='A'
        )
        ans2.check_answer()

        score = submission.calculate_score()
        self.assertEqual(score, 100.0)


class SubmissionViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Password123!'
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password=self.password,
            role=User.ROLE_STUDENT
        )
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.worksheet = Worksheet.objects.create(
            author=self.teacher,
            title='Kimya Testi'
        )

    def test_my_submissions_view(self):
        self.client.login(email='student@example.com', password=self.password)
        response = self.client.get(reverse('my_submissions'))
        self.assertEqual(response.status_code, 200)

    def test_submission_detail_view(self):
        submission = Submission.objects.create(
            student=self.student,
            worksheet=self.worksheet,
            score=80.0
        )
        self.client.login(email='student@example.com', password=self.password)
        response = self.client.get(reverse('submission_detail', kwargs={'pk': submission.pk}))
        self.assertEqual(response.status_code, 200)
