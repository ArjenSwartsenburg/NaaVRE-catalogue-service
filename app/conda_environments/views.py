from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
import uuid

from base_assets.views import BaseAssetViewSet
from file_assets.services.s3storage import S3StorageService
from . import models
from . import serializers


class CondaEnvironmentViewSet(BaseAssetViewSet):
    queryset = models.CondaEnvironment.objects.all()
    serializer_class = serializers.CondaEnvironmentSerializer
    model_class = models.CondaEnvironment

    def __init__(self, **kwargs):
        self.s3_service = S3StorageService()
        super().__init__(**kwargs)

    @action(methods=['post'], detail=False, serializer_class=serializers.PresignRequestSerializer)
    def presign(self, request):
        """ Generate a presigned URL for direct upload to S3.

        Expected input: {"filename": "environment.tar.gz", "content_type": "application/gzip"}

        Returns:
            `key`: S3 object key (i.e. the path in the bucket)
            `url`: a presigned upload URL
        """
        serializer = serializers.PresignRequestSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                serializer.errors, status=status.HTTP_400_BAD_REQUEST
                )

        filename = serializer.validated_data["filename"]
        content_type = serializer.validated_data["content_type"]

        filename = filename.replace('/', '_')
        filename = models.CondaEnvironmentFile.file.field.generate_filename(
            None,
            f"{uuid.uuid4()}_{filename}",
            )

        key, url = self.s3_service.generate_presigned_upload_url(
            filename,
            content_type,
            )

        return Response({
            "key": key,
            "url": url,
        })

    def perform_create(self, serializer):
        super().perform_create(serializer)
