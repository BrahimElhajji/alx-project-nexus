from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Category, JobPost, Application
from .serializers import (
    CategorySerializer,
    JobPostSerializer,
    JobPostCreateUpdateSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer
)
from .permissions import IsEmployer, IsJobSeeker, IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.response import Response

@api_view(['GET'])
def ping(request):
    return Response({'pong': True})

# Category list/create
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated, IsEmployer]

# JobPost CRUD for employers
class JobPostCreateView(generics.CreateAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

class JobPostListView(generics.ListAPIView):
    queryset = JobPost.objects.select_related('category', 'employer').all()
    serializer_class = JobPostSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'company_name', 'location', 'category__name']
    ordering_fields = ['created_at', 'title']

class JobPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobPost.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    serializer_class = JobPostSerializer

    def get_serializer_class(self):
        if self.request.method in [PUT, PATCH]:
            return JobPostCreateUpdateSerializer
        return JobPostSerializer

# Applying to jobs (job seeker)
class ApplyJobView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def perform_create(self, serializer):
        job_id = self.request.data.get("job")
        if job_id is None:
            raise serializers.ValidationError({"job": "This field is required."})
        job = get_object_or_404(JobPost, pk=job_id)
        serializer.save(applicant=self.request.user, job=job)

# Employer viewing their applications
class EmployerApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]

    def get_queryset(self):
        return Application.objects.filter(job__employer=self.request.user).select_related('applicant', 'job')

# Job seeker viewing their applications
class SeekerApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).select_related('job')
