from django.db import models

from base_assets.models import BaseAsset


class CondaEnvironment(BaseAsset):
    environment_name = models.CharField(max_length=255, blank=True)
    python_version = models.CharField(max_length=50, blank=True)
    package_count = models.IntegerField(default=0)
    created_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.title}-{self.owner.username}'

    def delete(self, *args, **kwargs):
        # Cascade deletion to files and S3 storage handled by on_delete=CASCADE
        super().delete(*args, **kwargs)


class CondaEnvironmentFile(models.Model):
    FILE_TYPE_CHOICES = [
        ('environment_tar', 'Environment TAR archive'),
        ('requirements_list', 'Requirements.txt file'),
    ]

    conda_environment = models.ForeignKey(
        CondaEnvironment,
        related_name='files',
        on_delete=models.CASCADE,
    )
    file = models.FileField(upload_to='conda_environments/')
    file_type = models.CharField(max_length=50, choices=FILE_TYPE_CHOICES)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']
        unique_together = ('conda_environment', 'file_type')

    def __str__(self):
        return f'{self.conda_environment.title}-{self.file_type}'

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        if self.file.name:
            self.file.storage.delete(self.file.name)
