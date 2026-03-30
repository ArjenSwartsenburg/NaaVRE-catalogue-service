from django.contrib import admin

from . import models


class CondaEnvironmentFileInline(admin.TabularInline):
    model = models.CondaEnvironmentFile
    fields = ['file_type', 'order', 'file']
    extra = 0


@admin.register(models.CondaEnvironment)
class CondaEnvironmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'environment_name', 'python_version', 'package_count', 'created']
    list_filter = ['owner', 'created', 'virtual_lab']
    search_fields = ['title', 'description', 'environment_name']
    readonly_fields = ['id', 'created', 'modified', 'owner']
    inlines = [CondaEnvironmentFileInline]
    fieldsets = (
        ('Basic Info', {
            'fields': ('id', 'title', 'description', 'owner', 'virtual_lab')
        }),
        ('Environment Metadata', {
            'fields': ('environment_name', 'python_version', 'package_count', 'created_date')
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


@admin.register(models.CondaEnvironmentFile)
class CondaEnvironmentFileAdmin(admin.ModelAdmin):
    list_display = ['conda_environment', 'file_type', 'order']
    list_filter = ['file_type', 'conda_environment']
    readonly_fields = ['id']
