# tasks/serializers.py
from rest_framework import serializers
from .models import Task
from django.utils.translation import gettext_lazy as _

class UserTaskUpdateSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(
        choices=Task.Status.choices,
        help_text=_("Task status: TODO, IN_PROGRESS, or DONE")
    )

    class Meta:
        model = Task
        fields = ['status']
        read_only_fields = ['title', 'description', 'created_at', 'updated_at', 'due_date']
        extra_kwargs = {
            'status': {'required': True}
        }

    def validate_status(self, value):
        valid_statuses = [choice[0] for choice in Task.Status.choices]
        if value not in valid_statuses:
            raise serializers.ValidationError(
                _("Invalid status. Allowed values: %(valid_statuses)s") % {
                    'valid_statuses': ', '.join(valid_statuses)
                }
            )
        return value

class TaskSerializer(serializers.ModelSerializer):
    status = serializers.ChoiceField(choices=Task.Status.choices)
    created_by = serializers.StringRelatedField()
    assigned_to = serializers.StringRelatedField()

    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['created_by', 'created_at', 'updated_at']