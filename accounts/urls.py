# accounts/urls.py
from django.urls import path
from .views import*

urlpatterns = [
    path('register/', UserRegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('CreateTeacher/',TeacherRegisterView.as_view(), name='teacher-register'),
    path('change-password/', PasswordChangeView.as_view(), name='change-password'),

]