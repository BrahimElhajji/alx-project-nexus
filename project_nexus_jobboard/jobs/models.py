from django.db import models
from django.conf import settings
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class JobPost(models.Model):
    EMPLOYMENT_TYPE = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    )

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField()
    company_name = models.CharField(max_length=255, db_index=True)
    location = models.CharField(max_length=255, db_index=True)
    category = models.ForeignKey(Category, related_name='jobs', on_delete=models.SET_NULL, null=True)
    employment_type = models.CharField(max_length=50, choices=EMPLOYMENT_TYPE)
    employer = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='posted_jobs', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['location']),
            models.Index(fields=['company_name']),
            models.Index(fields=['employment_type']),
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} @ {self.company_name}'


class Application(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    job = models.ForeignKey(JobPost, related_name='applications', on_delete=models.CASCADE)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='applications', on_delete=models.CASCADE)
    cover_letter = models.TextField(blank=True)
    resume_url = models.URLField(blank=True)  # or FileField if you plan upload
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('job', 'applicant')
        ordering = ['-applied_at']

    def __str__(self):
        return f'{self.applicant.username} -> {self.job.title}'


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    url = models.URLField(blank=True, null=True)  # Optional link to the related resource
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification for {self.user} - Read: {self.is_read}"
# Create your models here.
