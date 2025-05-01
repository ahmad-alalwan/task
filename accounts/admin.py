from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.html import format_html
from .models import User, UserToken, TeacherProfile, UserProfile

class UserTokenInline(admin.TabularInline):
    model = UserToken
    extra = 0
    readonly_fields = ('token_preview', 'created_at', 'expires_at')
    
    def token_preview(self, obj):
        return format_html(
            '<div style="font-family: monospace; word-break: break-all; background: #f8f8f8; padding: 8px; border-radius: 4px;">'
            '<strong>Access Token:</strong><br>{}<br><br>'
            '<strong>Refresh Token:</strong><br>{}'
            '</div>',
            obj.access_token[:100] + '...' if len(obj.access_token) > 100 else obj.access_token,
            obj.refresh_token[:100] + '...' if len(obj.refresh_token) > 100 else obj.refresh_token
        )
    token_preview.short_description = 'Tokens'

class CustomUserAdmin(UserAdmin):
    inlines = [UserTokenInline]
    list_display = ('email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ('last_login',) 
    admin_fieldsets = (
    (None, {'fields': ('email', 'password')}),
    ('Personal info', {'fields': ('first_name', 'last_name')}),
    ('Permissions', {
        'fields': ('is_active', 'is_staff', 'is_superuser', 'role', 'groups', 'user_permissions'),
    }),
    ('Important dates', {'fields': ('last_login',)}),  
)

    teacher_fieldsets = (
        (None, {'fields': ('email',)}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Status', {'fields': ('is_active', 'role')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'role', 'is_staff', 'is_active'),
        }),
    )

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets
            
        if request.user.role == User.Role.TEACHER and obj.role == User.Role.USER:
            return self.admin_fieldsets
        elif request.user.role == User.Role.TEACHER:
            return self.teacher_fieldsets
        return self.admin_fieldsets

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        if not obj:
            return readonly_fields
            
        if request.user.role == User.Role.TEACHER and obj.role == User.Role.USER:
            return ()
        elif request.user.role == User.Role.TEACHER:
            return readonly_fields + ('is_staff', 'is_superuser', 'groups', 'user_permissions')
        return readonly_fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == User.Role.TEACHER:
            return qs.exclude(role=User.Role.ADMIN)
        return qs

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if request.user.role == User.Role.TEACHER:
            form.base_fields['role'].choices = [
                (User.Role.USER, 'User'),
                (User.Role.TEACHER, 'Teacher')
            ]
        return form

    def has_change_permission(self, request, obj=None):
        if obj and request.user.role == User.Role.TEACHER:
            return obj.role in [User.Role.USER, User.Role.TEACHER]
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and request.user.role == User.Role.TEACHER:
            return obj.role == User.Role.USER
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        if request.user.role == User.Role.TEACHER:
            if obj.role == User.Role.ADMIN:
                obj.role = User.Role.USER
            obj.is_staff = False
            obj.is_superuser = False
        super().save_model(request, obj, form, change)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

@admin.register(UserToken)
class UserTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'expires_at')
    readonly_fields = ('user', 'refresh_token', 'access_token', 'created_at', 'expires_at')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'qualification')

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    # Only show UserProfiles where the user's role is 'USER'
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(user__role=User.Role.USER)  # Filter only USER role

    list_display = ['user_email', 'education_level']
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = 'User Email'  # Custom column name

