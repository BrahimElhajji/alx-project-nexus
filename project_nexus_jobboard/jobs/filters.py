import django_filters
from .models import Application

class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='iexact')
    applicant = django_filters.CharFilter(field_name='applicant__username', lookup_expr='icontains')
    applied_after = django_filters.DateFilter(field_name='applied_at', lookup_expr='gte')
    applied_before = django_filters.DateFilter(field_name='applied_at', lookup_expr='lte')
    job_title = django_filters.CharFilter(field_name="job__title", lookup_expr="icontains")

    class Meta:
        model = Application
        fields = ['status', 'applicant', 'applied_after', 'applied_before', 'job_title']
