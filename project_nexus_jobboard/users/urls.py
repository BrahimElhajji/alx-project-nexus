from django.urls import path, include
from .views import RegisterUserView, SignupView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('signup/', SignupView.as_view(), name='signup'),
]
