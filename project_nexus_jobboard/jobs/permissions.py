
from rest_framework import permissions
from rest_framework.permissions import BasePermission

class IsEmployerOfJobApplication(BasePermission):
    def has_object_permission(self, request, view, obj):
        # Only employer who owns the job related to this application can update status
        return request.user == obj.job.employer

class IsEmployer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_employer", False))

class IsJobSeeker(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and getattr(request.user, "is_job_seeker", False))

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "employer"):
            return obj.employer == request.user
        return False
