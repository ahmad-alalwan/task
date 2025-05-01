from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class CustomUserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    def create_teacher(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)  
        extra_fields.setdefault('role', self.model.Role.TEACHER)
        return self._create_user(email, password, **extra_fields)

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TEACHER = 'TEACHER', 'Teacher'
        USER = 'USER', 'User'
    
    email = models.EmailField(unique=True)  

    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.USER)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    def generate_tokens(self):
        return UserToken.create_for_user(self)
    def has_perm(self, perm, obj=None):
        if self.role == self.Role.TEACHER and self.is_staff:
            return True
        return super().has_perm(perm, obj)

    def has_module_perms(self, app_label):
        if self.role == self.Role.TEACHER and self.is_staff:
            return True
        return super().has_module_perms(app_label)
    def has_perm(self, perm, obj=None):
        if self.role == self.Role.TEACHER:
            return perm in ['accounts.view_userprofile']
        return super().has_perm(perm, obj)
    def save(self, *args, **kwargs):
        if self.role == User.Role.ADMIN:
            UserProfile.objects.filter(user=self).delete()
        super().save(*args, **kwargs)
    def can_assign_user_role(self):
        """Teachers can assign USER role if they are staff members."""
        return self.role == self.Role.TEACHER and self.is_staff
    class Meta:
        permissions = [
            ('can_manage_users', 'Can manage regular users'),
            ('can_promote_to_teacher', 'Can promote users to teacher role'),
        ]

class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher_profile')
    subject = models.CharField(max_length=100)
    qualification = models.CharField(max_length=200)
    bio = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.user.email}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    interests = models.TextField(blank=True)
    education_level = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"{self.user.email}"
class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tokens')
    refresh_token = models.TextField()
    access_token = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Tokens for {self.user.email} (expires: {self.expires_at})"

    @classmethod
    def create_for_user(cls, user):
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        expires_at = datetime.fromtimestamp(refresh.access_token.payload['exp'])
        
        return cls.objects.create(
            user=user,
            refresh_token=refresh_token,
            access_token=access_token,
            expires_at=expires_at
        )
class PasswordChangeToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=15)  # 15 minute expiry
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at
