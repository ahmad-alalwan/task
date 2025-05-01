from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from accounts.models import User

User = get_user_model()

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = 'TODO', _('To Do')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        DONE = 'DONE', _('Done')

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='task_created_tasks'  # Changed
    )
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,  # Changed from SET_NULL to enforce user links
        related_name='task_assigned_tasks'  # Changed
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
        constraints = [
            models.CheckConstraint(
                check=models.Q(status__in=['TODO', 'IN_PROGRESS', 'DONE']),
                name="valid_task_status"
            )
        ]

    def __str__(self):
        return f"{self.title} (Assigned to: {self.assigned_to.email})"