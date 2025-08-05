from rest_framework import generics, filters, status
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import django_filters
from django_filters.rest_framework import FilterSet
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


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


@api_view(['GET'])
def ping(request):
    return Response({'pong': True})


# Category list/create
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permission(self);
    if self.request.method == "POST":
        return [IsAuthenticated(), IsEmployer()]
    return[] # public Get


# JobPost CRUD for employers
class JobPostCreateView(generics.CreateAPIView):
    queryset = JobPost.objects.all()
    serializer_class = JobPostCreateUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployer]


    @swagger_auto_schema(
        operation_description="Create a job post (employers only).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "description", "company_name", "location", "employment_type"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING),
                "description": openapi.Schema(type=openapi.TYPE_STRING),
                "company_name": openapi.Schema(type=openapi.TYPE_STRING),
                "location": openapi.Schema(type=openapi.TYPE_STRING),
                "employment_type": openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=["full_time", "part_time", "contract", "internship"]
                ),
                "category": openapi.Schema(type=openapi.TYPE_INTEGER),
            },
        ),
        responses={201: openapi.Response("Created", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(employer=self.request.user)

class JobPostFilter(FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    location = django_filters.CharFilter(lookup_expr="icontains")
    employment_type = django_filters.CharFilter()

    class Meta:
        model = JobPost
        fields = ["category", "location", "employment_type"]

class JobPostListView(generics.ListAPIView):
    queryset = JobPost.objects.select_related('category', 'employer').all()
    serializer_class = JobPostSerializer
    filterset_class = JobPostFilter
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'company_name', 'location', 'category__name']
    ordering_fields = ['created_at', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
            operation_description="List job posts with optional filtering by category, location, employment type, search, and ordering.",
            manual_parameters=[]  # drf-yasg will infer from filterset/search/ordering
            security=[],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
 
class JobPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobPost.objects.all()
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ["PUT", "PATCH"]:
            return JobPostCreateUpdateSerializer
        return JobPostSerializer

# Applying to jobs (job seeker)
class ApplyJobView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationCreateSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]


    @swagger_auto_schema(
        operation_description="Submit an application to a job (job seekers only).",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["job", "cover_letter", "resume_url"],
            properties={
                "job": openapi.Schema(type=openapi.TYPE_INTEGER),
                "cover_letter": openapi.Schema(type=openapi.TYPE_STRING),
                "resume_url": openapi.Schema(type=openapi.TYPE_STRING, format="uri"),
            },
        ),
        responses={201: openapi.Response("Created", schema=openapi.Schema(type=openapi.TYPE_OBJECT))},
        security=[{"Bearer": []}],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        job_id = self.request.data.get("job")
        if job_id is None:
            from rest_framework import serializers as drf_serializers
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
