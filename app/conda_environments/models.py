from django.db import models

from base_assets.models import BaseAsset


class CondaEnvironment(BaseAsset):
    environment_name = models.CharField(max_length=255, blank=True)
    python_version = models.CharField(max_length=50, blank=True)
    package_count = models.IntegerField(default=0)
    created_date = models.DateTimeField(null=True, blank=True)
    environment_file = models.FileField(upload_to='conda_environments/', unique=True, null=True, blank=True)
    dependency_list = models.FileField(upload_to='dependency_lists/', unique=True, null=True, blank=True)

    def __str__(self):
        return f'{self.title}-{self.owner.username}'

    def delete(self, *args, **kwargs):
        # Clean up S3 files before deletion
        if self.environment_file.name:
            self.environment_file.storage.delete(self.environment_file.name)
        if self.dependency_list.name:
            self.dependency_list.storage.delete(self.dependency_list.name)
        super().delete(*args, **kwargs)

