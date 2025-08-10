
from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse  # Add this import
from jobs.models import JobPost, Category

User = get_user_model()

class JobPostAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        # Create test user
        self.user = User.objects.create_user(
            username='employeruser',
            password='YourPass123',
            email='employer@example.com',
            is_employer=True,  # Fix: use the actual field name
            is_job_seeker=False
        )

        # Log in and get token
        login_response = self.client.post(
            "/api/token/",
            {"username": "employeruser", "password": "YourPass123"},
            format="json"
        )
        
        if login_response.status_code == 200:
            self.token = login_response.data["access"]
            # Set authorization header
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Create category
        self.category = Category.objects.create(
            name="Software Development",
            slug="software-development"
        )

    def test_create_job_post(self):
        url = '/api/jobs/create/'  # Use explicit URL since reverse might not work
        data = {
            "title": "Backend Developer",
            "description": "Build APIs",
            "company_name": "MyCompany",
            "location": "Remote",
            "employment_type": "full_time",
            "category": self.category.id
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
        url = "/api/jobs/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
