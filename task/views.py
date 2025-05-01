from rest_framework.pagination import PageNumberPagination
from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.response import Response
from django.utils.translation import gettext_lazy as _
from .models import Task
from .serializers import *
from rest_framework.decorators import api_view 
from accounts.models import User
from django.db import models


class TaskStatusUpdateView(generics.UpdateAPIView):
    serializer_class = UserTaskUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Task.objects.all()
    http_method_names = ['patch']  

    def get_object(self):
        task = super().get_object()
        if task.assigned_to != self.request.user:
            raise PermissionDenied(
                _("You can only update status of tasks assigned to you")
            )
        return task

    def patch(self, request, *args, **kwargs):
        task = self.get_object()
        serializer = self.get_serializer(task, data=request.data, partial=True)
        
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            return Response({
                "success": True,
                "message": _("Task status updated successfully"),
                "task": {
                    "id": task.id,
                    "title": task.title,
                    "previous_status": task.status,
                    "new_status": serializer.validated_data['status'],
                    "assigned_to": task.assigned_to.email
                }
            })
            
        except ValidationError as e:
            return Response({
                "success": False,
                "error": _("Validation error"),
                "details": e.detail,
                "allowed_statuses": dict(Task.Status.choices)
            }, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def Task_user(request, email):
    try:
        user = User.objects.get(email=email)
        tasks = Task.objects.filter(
            models.Q(created_by=user) | models.Q(assigned_to=user)
        ).order_by('-created_at')
        
        paginator = PageNumberPagination()
        paginator.page_size = 10
        result_page = paginator.paginate_queryset(tasks, request)
        
        user_info = {
            'email': user.email,
            
        }
        
        if hasattr(user, 'username'):
            user_info['username'] = user.username
            
        serializer = TaskSerializer(result_page, many=True)
        return paginator.get_paginated_response({
            'user': user_info,
            'tasks': serializer.data
        })
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
        
