# tasks/urls.py
from django.urls import path
from . import views 

urlpatterns = [
    path('tasks/<str:email>/', views.Task_user, name='task-status-update'),


]