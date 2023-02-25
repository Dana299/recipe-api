import boto3
from django.conf import settings
from django.db.models.signals import pre_delete
from django.dispatch import receiver

from .models import Image


@receiver(pre_delete, sender=Image)
def image_file_delete(sender, instance, **kwargs):
    """
    Reacts on deleting the record in Image DB and deletes
    corresponding file from cloud storage.
    """

    s3 = boto3.resource(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
    )

    bucket = s3.Bucket(settings.AWS_STORAGE_BUCKET_NAME)

    # get file key depending on its status in DB
    if instance.is_temporary:
        directory = settings.AWS_LOCATION
    else:
        directory = settings.AWS_PERMANENT_DIRECTORY

    key = directory + instance.image.name

    bucket.delete_objects(Delete={'Objects': [{'Key': key}]})