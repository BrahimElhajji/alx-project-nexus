
from django.urls import path
from .views import (
    ping,
    CategoryListCreateView,
    JobPostCreateView,
    JobPostListView,
    JobPostDetailView,
    ApplyJobView,
    EmployerApplicationsView,
    SeekerApplicationsView,
    ApplicationStatusUpdateView,
    NotificationListView,
    NotificationMarkReadView,
    NotificationUnreadCountView
)
from . import views

urlpatterns = [
    path('ping/', ping, name='ping'),
    path('categories/', CategoryListCreateView.as_view(), name='categories'),
    path('jobs/', JobPostListView.as_view(), name='job-list'),
    path('jobs/create/', JobPostCreateView.as_view(), name='job-create'),
    path('jobs/<int:pk>/', JobPostDetailView.as_view(), name='job-detail'),
    path('applications/apply/', ApplyJobView.as_view(), name='apply-job'),
    path('applications/employer/', EmployerApplicationsView.as_view(), name='employer-apps'),
    path('applications/seeker/', SeekerApplicationsView.as_view(), name='seeker-apps'),
    path('applications/<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status-update'),
    path('notifications/', NotificationListView.as_view(), name='notifications-list'),
    path('notifications/<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('notifications/unread_count/', NotificationUnreadCountView.as_view(), name='notifications-unread-count'),
]
