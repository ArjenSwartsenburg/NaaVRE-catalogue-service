from django.contrib import admin

from . import models


@admin.register(models.CondaEnvironment)
class CondaEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'environment_name', 'python_version', 'package_count', 'created']
    list_filter = ['owner', 'created', 'virtual_lab']
    search_fields = ['title', 'description', 'environment_name']
    readonly_fields = ['id', 'created', 'modified', 'owner']
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'title', 'description', 'owner', 'virtual_lab')
        }),
        ('Environment Metadata', {
            'fields': ('environment_name', 'python_version', 'package_count', 'created_date')
        }),
        ('Files', {
            'fields': ('environment_file', 'dependency_list'),
            'description': 'Conda environment must include both the tar archive and dependencies file'
        }),
        ('Sharing', {
            'fields': ('shared_with_scopes', 'shared_with_users')
        }),
        ('Timestamps', {
            'fields': ('created', 'modified')
        }),
    )

    def save_model(self, request, obj, form, change):
        if not change:
            obj.owner = request.user
        super().save_model(request, obj, form, change)
