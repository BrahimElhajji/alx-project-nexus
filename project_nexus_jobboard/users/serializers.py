from rest_framework import serializers, status
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    role = serializers.ChoiceField(choices=[('employer', 'Employer'), ('job_seeker', 'Job Seeker')], write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_employer', 'is_job_seeker', 'role']
        read_only_fields = ['is_employer', 'is_job_seeker']

    def create(self, validated_data):
        role = validated_data.pop('role')
        password = validated_data.pop('password')
        user = User(**validated_data)

        if role == 'employer':
            user.is_employer = True
            user.is_job_seeker = False
        elif role == 'job_seeker':
            user.is_employer = False
            user.is_job_seeker = True

        user.set_password(password)
        user.save()
        return user
