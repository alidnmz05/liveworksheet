from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from apps.assignments.models import Assignment
from apps.accounts.models import Classroom
from apps.worksheets.models import Worksheet

User = get_user_model()


class AssignmentModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password='Password123!',
            role=User.ROLE_TEACHER
        )
        self.worksheet = Worksheet.objects.create(
            author=self.teacher,
            title='Odev Calismasi'
        )

    def test_assignment_is_overdue(self):
        past_date = timezone.now() - timedelta(days=2)
        future_date = timezone.now() + timedelta(days=2)

        past_assignment = Assignment.objects.create(
            created_by=self.teacher,
            title='Gecmis Odev',
            worksheet=self.worksheet,
            due_date=past_date
        )
        future_assignment = Assignment.objects.create(
            created_by=self.teacher,
            title='Gelecek Odev',
            worksheet=self.worksheet,
            due_date=future_date
        )

        self.assertTrue(past_assignment.is_overdue)
        self.assertFalse(future_assignment.is_overdue)


class AssignmentViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.password = 'Password123!'
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            password=self.password,
            role=User.ROLE_TEACHER
        )
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password=self.password,
            role=User.ROLE_STUDENT
        )
        self.classroom = Classroom.objects.create(
            teacher=self.teacher,
            name='10-B'
        )
        self.classroom.students.add(self.student)
        self.worksheet = Worksheet.objects.create(
            author=self.teacher,
            title='Matematik Test 1'
        )

    def test_assignment_create_view_by_teacher(self):
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.post(reverse('assignment_create'), {
            'title': 'Haftalık Ödev',
            'worksheet_id': str(self.worksheet.id),
            'classroom_ids': [self.classroom.id],
            'allow_multiple_attempts': 'on',
            'show_answers': 'on'
        })
        self.assertEqual(response.status_code, 302)
        assignment = Assignment.objects.get(title='Haftalık Ödev')
        self.assertEqual(assignment.worksheet, self.worksheet)
        self.assertTrue(assignment.allow_multiple_attempts)

    def test_assignment_create_restricted_for_students(self):
        self.client.login(email='student@example.com', password=self.password)
        response = self.client.get(reverse('assignment_create'))
        self.assertEqual(response.status_code, 302)  # Redirects to dashboard

    def test_assignment_list_for_teacher_and_student(self):
        assignment = Assignment.objects.create(
            created_by=self.teacher,
            title='Sınıf Ödevi',
            worksheet=self.worksheet
        )
        assignment.classrooms.add(self.classroom)

        # Teacher list
        self.client.login(email='teacher@example.com', password=self.password)
        response_teacher = self.client.get(reverse('assignment_list'))
        self.assertEqual(response_teacher.status_code, 200)

        # Student list
        self.client.login(email='student@example.com', password=self.password)
        response_student = self.client.get(reverse('assignment_list'))
        self.assertEqual(response_student.status_code, 200)

    def test_assignment_detail_access(self):
        assignment = Assignment.objects.create(
            created_by=self.teacher,
            title='Detay Ödevi',
            worksheet=self.worksheet
        )
        self.client.login(email='teacher@example.com', password=self.password)
        response = self.client.get(reverse('assignment_detail', kwargs={'pk': assignment.pk}))
        self.assertEqual(response.status_code, 200)
