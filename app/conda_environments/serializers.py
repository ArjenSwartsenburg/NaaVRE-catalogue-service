from rest_framework import serializers

from base_assets.serializers import BaseAssetSerializer
from file_assets.services.s3storage import S3StorageService
from . import models


def key_exists_in_s3(key):
    if not S3StorageService().exists(key):
        raise serializers.ValidationError(
            'no object with this key exists in the bucket'
            )


class CondaEnvironmentSerializer(BaseAssetSerializer):
    environment_file_key = serializers.CharField(
        write_only=True,
        required=False,
        validators=[key_exists_in_s3],
    )
    dependency_list_key = serializers.CharField(
        write_only=True,
        required=False,
        validators=[key_exists_in_s3],
    )

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
            'environment_file',
            'dependency_list',
            'environment_file_key',
            'dependency_list_key',
        ]
        read_only_fields = ['environment_file', 'dependency_list']

    def validate(self, attrs):
        environment_name = attrs.get('environment_name')
        owner = self.context['request'].user
        qs = models.CondaEnvironment.objects.filter(
            environment_name=environment_name,
            owner=owner,
        )
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError({
                'environment_name':
                    'An environment with this name already exists for this owner.'
            })
        return attrs

    def create(self, validated_data):
        environment_file_key = validated_data.pop('environment_file_key', None)
        dependency_list_key = validated_data.pop('dependency_list_key', None)

        conda_env = models.CondaEnvironment(**validated_data)
        if environment_file_key:
            conda_env.environment_file.name = environment_file_key
        if dependency_list_key:
            conda_env.dependency_list.name = dependency_list_key
        conda_env.save()
        return conda_env

    def update(self, instance, validated_data):
        environment_file_key = validated_data.pop('environment_file_key', None)
        dependency_list_key = validated_data.pop('dependency_list_key', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if environment_file_key:
            instance.environment_file.name = environment_file_key
        if dependency_list_key:
            instance.dependency_list.name = dependency_list_key
        instance.save()
        return instance


class PresignRequestSerializer(serializers.Serializer):
    filename = serializers.CharField()
    content_type = serializers.RegexField(r'^\w+/[-+.\w]+$')

