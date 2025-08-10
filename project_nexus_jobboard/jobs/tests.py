from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from jobs.models import JobPost, Category
from users.models import User 

User = get_user_model()

class JobPostAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='employeruser',
            password='YourPass123',
            email='employer@example.com',
            role='employer'
        )
        self.client.login(username='employeruser', password='YourPass123')

        # Log in and get token
        login_response = self.client.post(
            "/api/token/",
            {"username": "employeruser", "password": "YourPass123"},
            format="json"
        )
        self.token = login_response.data["access"]

        # Set authorization header
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create category
        self.category = Category.objects.create(
            name="Software Development",
            slug="software-development"
        )

    def test_create_job_post(self):
        url = reverse('job-create')  # Adjust if needed
        data = {
            "title": "Backend Developer",
            "description": "Build APIs",
            "company_name": "MyCompany",
            "location": "Remote",
            "employment_type": "full_time",
            "category": 1
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_list_job_posts(self):
        JobPost.objects.create(
            title="Test Job",
            description="Test description",
            company_name="TestCompany",
            location="Remote",
            employment_type="full_time",
            category=self.category,
            employer=self.user
        )
        url = "/api/jobs/"  # Adjust if needed
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data.get("results", [])), 0)
