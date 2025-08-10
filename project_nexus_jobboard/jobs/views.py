from rest_framework import generics, filters, status, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import django_filters
from django_filters.rest_framework import FilterSet, DjangoFilterBackend
from .filters import ApplicationFilter
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from .models import Category, JobPost, Application, Notification
from .serializers import (
    CategorySerializer,
    JobPostSerializer,
    JobPostCreateUpdateSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
    NotificationSerializer
)
from django.db.models import Count
from .permissions import IsEmployer, IsJobSeeker, IsOwnerOrReadOnly, IsEmployerOfJobApplication
from rest_framework.decorators import api_view
from .pagination import StandardResultsSetPagination


@api_view(['GET'])
def ping(request):
    return Response({'pong': True})


# Category list/create
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_permissions(self):
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

class JobPostFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name="category__id")
    location = django_filters.CharFilter(lookup_expr="icontains")
    employment_type = django_filters.CharFilter()
    company_name = django_filters.CharFilter(lookup_expr="icontains")
    created_at_after = django_filters.DateFilter(field_name="created_at", lookup_expr='gte')
    created_at_before = django_filters.DateFilter(field_name="created_at", lookup_expr='lte')

    class Meta:
        model = JobPost
        fields = [
            "category",
            "location",
            "employment_type",
            "company_name",
            "created_at_after",
            "created_at_before",
        ]

class JobPostListView(generics.ListAPIView):
    # Swagger parameters
    location_param = openapi.Parameter(
        'location', openapi.IN_QUERY, description="Filter by job location",
        type=openapi.TYPE_STRING
    )
    category_param = openapi.Parameter(
        'category', openapi.IN_QUERY, description="Filter by category ID",
        type=openapi.TYPE_INTEGER
    )
    type_param = openapi.Parameter(
        'job_type', openapi.IN_QUERY, description="Filter by job type (Full-time, Part-time, etc.)",
        type=openapi.TYPE_STRING
    )
    company_param = openapi.Parameter(
            'company_name', openapi.IN_QUERY, description="Filter by company name (partial match)",
            type=openapi.TYPE_STRING
    )
    created_after_param = openapi.Parameter(
            'created_at_after', openapi.IN_QUERY, description="Filter jobs created on or after this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING, format='date'
            )
    created_before_param = openapi.Parameter(
            'created_at_before', openapi.IN_QUERY, description="Filter jobs created on or before this date (YYYY-MM-DD)",
            type=openapi.TYPE_STRING, format='date'
            )

    queryset = JobPost.objects.select_related('category', 'employer').all()
    serializer_class = JobPostSerializer
    filterset_class = JobPostFilter
    filter_backends = [
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    ]
    search_fields = ['title', 'description', 'company_name', 'location', 'category__name']
    ordering_fields = ['created_at', 'title']
    permission_classes = [IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="List job posts with optional filtering by category, location, employment type, search, and ordering.",
        manual_parameters=[location_param, category_param, type_param, company_param, created_after_param, created_before_param],
        security=[],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    pagination_class = StandardResultsSetPagination
 
class JobPostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JobPost.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

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
        job_id = self.request.data.get('job')
        job = get_object_or_404(JobPost, id=job_id)

        # Check for existing application
        if Application.objects.filter(job=job, applicant=self.request.user).exists():
            raise ValidationError({"detail": "You have already applied to this job."})

        application = serializer.save(applicant=self.request.user, job=job)
        
        # Create notification for employer
        Notification.objects.create(
                user=job.employer,
                message=f"New application for {job.title}",
                url=f"http://localhost:8000/applications/{application.id}"
                )

class EmployerApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsEmployer]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApplicationFilter

    def get_queryset(self):
        return Application.objects.filter(job__employer=self.request.user).select_related('applicant', 'job')

    pagination_class = StandardResultsSetPagination

# Job seeker viewing their applications
class SeekerApplicationsView(generics.ListAPIView):
    serializer_class = ApplicationSerializer
    permission_classes = [IsAuthenticated, IsJobSeeker]
    filter_backends = [DjangoFilterBackend]
    filterset_class = ApplicationFilter

    def get_queryset(self):
        return Application.objects.filter(applicant=self.request.user).select_related('job')

    pagination_class = StandardResultsSetPagination


class ApplicationStatusUpdateView(generics.UpdateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationStatusUpdateSerializer
    permission_classes = [IsAuthenticated, IsEmployerOfJobApplication]

    def patch(self, request, *args, **kwargs):
        application = self.get_object()
        new_status = request.data.get("status")

        if new_status not in ["pending", "reviewed", "accepted", "rejected"]:
            return Response({"error": "Invalid status"}, status=status.HTTP_400_BAD_REQUEST)

        application.status = new_status
        application.save()

        return Response({"status": application.status})


class NotificationListView(generics.ListAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.filter(user=self.request.user).order_by('-created_at')
        # support ?is_read=true/false or ?unread=true
        is_read = self.request.query_params.get('is_read')
        unread = self.request.query_params.get('unread')
        if unread is not None:
            if unread.lower() in ('1', 'true', 'yes'):
                qs = qs.filter(is_read=False)
        elif is_read is not None:
            if is_read.lower() in ('1', 'true', 'yes'):
                qs = qs.filter(is_read=True)
            else:
                qs = qs.filter(is_read=False)
        return qs

class NotificationMarkReadView(generics.UpdateAPIView):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Notification.objects.all()

    def get_queryset(self):
        # Ensure users can only update their own notifications
        return Notification.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        serializer = self.get_serializer(notification)
        return Response(serializer.data)

class NotificationUnreadCountView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        unread = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({"unread_count": unread})
