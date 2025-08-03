
from django.urls import path
from .views import (
    ping,
    CategoryListCreateView,
    JobPostCreateView,
    JobPostListView,
    JobPostDetailView,
    ApplyJobView,
    EmployerApplicationsView,
)

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('categories/', CategoryListCreateView.as_view(), name='categories'),
    path('jobs/', JobPostListView.as_view(), name='job-list'),
    path('jobs/create/', JobPostCreateView.as_view(), name='job-create'),
    path('jobs/<int:pk>/', JobPostDetailView.as_view(), name='job-detail'),
    path('applications/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('applications/employer/', EmployerApplicationsView.as_view(), name='employer-apps'),
]
