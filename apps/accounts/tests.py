from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.accounts.models import Classroom

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(
            username='teacher@example.com',
            email='teacher@example.com',
            first_name='Ali',
            last_name='Yılmaz',
            password='Password123!',
            role=User.ROLE_TEACHER,
            school='Atatürk Lisesi'
        )
        self.student = User.objects.create_user(
            username='student@example.com',
            email='student@example.com',
            password='Password123!',
            role=User.ROLE_STUDENT
        )

    def test_user_creation_and_properties(self):
        self.assertEqual(str(self.teacher), 'teacher@example.com')
        self.assertTrue(self.teacher.is_teacher)
        self.assertFalse(self.teacher.is_student)
        self.assertEqual(self.teacher.full_name, 'Ali Yılmaz')

        self.assertTrue(self.student.is_student)
        self.assertFalse(self.student.is_teacher)

    def test_classroom_creation_auto_code(self):
        classroom = Classroom.objects.create(
            teacher=self.teacher,
            name='10-A Matematik'
        )
        self.assertTrue(len(classroom.code) == 8)
        self.assertIn('10-A Matematik', str(classroom))


class AccountsViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_password = 'Password123!'
        self.user = User.objects.create_user(
            username='testuser@example.com',
            email='testuser@example.com',
            password=self.user_password,
            role=User.ROLE_TEACHER
        )

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_get(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_view_post_success(self):
        response = self.client.post(reverse('register'), {
            'first_name': 'Ahmet',
            'last_name': 'Demir',
            'email': 'newstudent@example.com',
            'role': User.ROLE_STUDENT,
            'password1': 'Password123!',
            'password2': 'Password123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='newstudent@example.com').exists())

    def test_login_logout_view(self):
        # Login POST
        response = self.client.post(reverse('login'), {
            'email': 'testuser@example.com',
            'password': self.user_password
        })
        self.assertEqual(response.status_code, 302)

        # Dashboard when logged in
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

        # Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_classroom_create_and_join(self):
        self.client.login(email='testuser@example.com', password=self.user_password)
        
        # Create classroom
        response = self.client.post(reverse('classroom_create'), {
            'name': 'Fizik 101',
            'description': 'Temel Fizik Dersleri'
        })
        self.assertEqual(response.status_code, 302)
        classroom = Classroom.objects.get(name='Fizik 101')
        self.assertEqual(classroom.teacher, self.user)

        # Student joins classroom
        student = User.objects.create_user(
            username='student2@example.com',
            email='student2@example.com',
            password='Password123!',
            role=User.ROLE_STUDENT
        )
        self.client.login(email='student2@example.com', password='Password123!')
        join_response = self.client.post(reverse('join_classroom'), {
            'code': classroom.code
        })
        self.assertEqual(join_response.status_code, 302)
        self.assertTrue(classroom.students.filter(id=student.id).exists())
