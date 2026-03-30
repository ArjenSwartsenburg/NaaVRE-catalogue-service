from rest_framework import serializers

from base_assets.serializers import BaseAssetSerializer
from file_assets.services.s3storage import S3StorageService
from . import models


def key_exists_in_s3(key):
    if not S3StorageService().exists(key):
        raise serializers.ValidationError(
            'no object with this key exists in the bucket'
            )


def key_does_not_exist_in_db(key):
    qs = models.CondaEnvironmentFile.objects.filter(file=key)
    if qs.exists():
        raise serializers.ValidationError(
            'a record with this key already exists in the database'
            )


class CondaEnvironmentFileSerializer(serializers.ModelSerializer):
    key = serializers.CharField(
        write_only=True,
        validators=[key_exists_in_s3, key_does_not_exist_in_db],
    )

    class Meta:
        model = models.CondaEnvironmentFile
        fields = ['id', 'file_type', 'order', 'key', 'file']
        read_only_fields = ['file', 'id']

    def create(self, validated_data):
        key = validated_data.pop('key')
        file_obj = models.CondaEnvironmentFile(**validated_data)
        file_obj.file.name = key
        file_obj.save()
        return file_obj


class CondaEnvironmentSerializer(BaseAssetSerializer):
    files = CondaEnvironmentFileSerializer(many=True, read_only=True)

    class Meta(BaseAssetSerializer.Meta):
        model = models.CondaEnvironment
        fields = [
            'id',
            'url',
            'title',
            'description',
            'owner',
            'virtual_lab',
            'shared_with_scopes',
            'shared_with_users',
            'created',
            'modified',
            'environment_name',
            'python_version',
            'package_count',
            'created_date',
            'files',
        ]


class PresignRequestSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content_type = serializers.RegexField(r'^\w+/[-+.\w]+$')
