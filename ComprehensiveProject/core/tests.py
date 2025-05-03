from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Profile, Session, Message, Review

class TutoringSystemTests(TestCase):
    def setUp(self):
        # Create student user
        self.student_user = User.objects.create_user(
            username='student', password='studentpass', email='student@example.com'
        )
        self.student_profile = Profile.objects.create(
            user=self.student_user,
            is_tutor=False,
            bio='I am a student.',
        )
        # Create tutor user
        self.tutor_user = User.objects.create_user(
            username='tutor', password='tutorpass', email='tutor@example.com'
        )
        self.tutor_profile = Profile.objects.create(
            user=self.tutor_user,
            is_tutor=True,
            bio='I am a tutor.',
            hourly_rate=50.0
        )
        # Initialize client
        self.client = Client()

    def test_registration(self):
        response = self.client.post(
            reverse('register'),
            data={
                'username': 'newuser',
                'email': 'new@example.com',
                'password1': 'ComplexPass123',
                'password2': 'ComplexPass123',
                'is_tutor': False
            }
        )
        # Should redirect after successful registration
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_logout(self):
        # Login
        login = self.client.login(username='student', password='studentpass')
        self.assertTrue(login)
        # Access a login-required page
        response = self.client.get(reverse('tutor_search'))
        self.assertEqual(response.status_code, 200)
        # Logout
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_profile_update(self):
        self.client.login(username='student', password='studentpass')
        response = self.client.post(
            reverse('profile'),
            data={
                'bio': 'Updated bio',
                'hourly_rate': ''
            }
        )
        self.assertEqual(response.status_code, 302)
        self.student_profile.refresh_from_db()
        self.assertEqual(self.student_profile.bio, 'Updated bio')

    def test_tutor_search(self):
        self.client.login(username='student', password='studentpass')
        response = self.client.get(reverse('tutor_search'), data={'subject': '', 'min_rating': ''})
        self.assertEqual(response.status_code, 200)
        # Should contain tutor in context
        self.assertContains(response, 'tutor')

    def test_book_session_and_conflict(self):
        self.client.login(username='student', password='studentpass')
        start_time = timezone.now() + timezone.timedelta(days=1)
        end_time = start_time + timezone.timedelta(hours=1)
        # First booking should succeed
        response1 = self.client.post(
            reverse('book_session', args=[self.tutor_profile.pk]),
            data={'start_time': start_time, 'end_time': end_time}
        )
        self.assertEqual(response1.status_code, 302)
        self.assertEqual(Session.objects.count(), 1)
        # Attempt overlapping booking
        response2 = self.client.post(
            reverse('book_session', args=[self.tutor_profile.pk]),
            data={'start_time': start_time + timezone.timedelta(minutes=30), 'end_time': end_time + timezone.timedelta(hours=1)}
        )
        # Should show error and not create a new session
        self.assertEqual(Session.objects.count(), 1)
        self.assertContains(response2, 'Time conflict')

    def test_message_sending(self):
        self.client.login(username='student', password='studentpass')
        response = self.client.post(
            reverse('send_message', args=[self.tutor_profile.pk]),
            data={'content': 'Hello Tutor!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Message.objects.count(), 1)
        msg = Message.objects.first()
        self.assertEqual(msg.sender, self.student_user)
        self.assertEqual(msg.recipient, self.tutor_user)

    def test_review_submission(self):
        # Create a confirmed session
        session = Session.objects.create(
            student=self.student_profile,
            tutor=self.tutor_profile,
            start_time=timezone.now(),
            end_time=timezone.now() + timezone.timedelta(hours=1),
            status='confirmed'
        )
        self.client.login(username='student', password='studentpass')
        response = self.client.post(
            reverse('session_detail', args=[session.pk]),
            data={'rating': 4, 'comment': 'Great session!'}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)
        review = Review.objects.first()
        self.assertEqual(review.rating, 4)
        self.assertEqual(review.comment, 'Great session!')

    def test_admin_access(self):
        # Superuser access check
        admin_user = User.objects.create_superuser(
            username='admin', password='adminpass', email='admin@example.com'
        )
        self.client.login(username='admin', password='adminpass')
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 200)
