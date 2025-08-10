
from rest_framework import serializers
from .models import Category, JobPost, Application, Notification

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug']

class JobPostSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    employer = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = JobPost
        fields = [
            'id',
            'title',
            'description',
            'company_name',
            'location',
            'category',
            'employment_type',
            'employer',
            'created_at',
        ]

class JobPostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobPost
        fields = [
            'title',
            'description',
            'company_name',
            'location',
            'employment_type',
            'category',
        ]

class ApplicationSerializer(serializers.ModelSerializer):
    job = JobPostSerializer(read_only=True)
    applicant = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Application
        fields = [
            'id',
            'job',
            'applicant',
            'cover_letter',
            'resume_url',
            'status',
            'applied_at',
        ]
        read_only_fields = ["id", "job", "job_seeker", "created_at"]

class ApplicationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['job', 'cover_letter', 'resume_url', 'status']

        def validate_status(self, value):
            valid_choices = [choice[0] for choice in Application.STATUS_CHOICES]
            if value not in valid_choices:
                raise serializers.ValidationError(f"Invalid status '{value}'. Must be one of {valid_choices}.")
            return value

class ApplicationStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']

    def validate_status(self, value):
        valid_choices = [choice[0] for choice in Application.STATUS_CHOICES]
        if value not in valid_choices:
            raise serializers.ValidationError(f"Invalid status '{value}'. Must be one of {valid_choices}.")
        return value

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'url', 'is_read', 'created_at']
        read_only_fields = ['id', 'message', 'url', 'created_at']
