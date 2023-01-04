from storages.backends.s3boto3 import S3Boto3Storage

from myproject.settings import AWS_STORAGE_BUCKET_NAME


class ClientDocsStorage(S3Boto3Storage):
    bucket_name = AWS_STORAGE_BUCKET_NAME
    file_overwrite = False