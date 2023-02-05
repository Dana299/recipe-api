
# this script makes a query to the database once a day in order to
# find expired images with flag "is_temporary" = True, then goes to
# the storage and deletes them
from __future__ import annotations

import os
from datetime import datetime

import psycopg2
from boto3.session import Session
from django.utils import timezone
from dotenv import load_dotenv

load_dotenv()

AWS_STORAGE_BUCKET_NAME = 'recipebucket'
AWS_REGION = os.getenv('AWS_REGION')
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')


def delete_images_from_storage(images) -> None:

    session = Session()

    s3 = session.client(
        region_name=AWS_REGION,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        service_name='s3',
        endpoint_url='https://storage.yandexcloud.net',
    )

    for image in images:
        image_name = image[0]
        s3.delete_object(
            Bucket=AWS_STORAGE_BUCKET_NAME,
            Key='temporary/' + image_name
        )


def get_expired_images() -> list[tuple]:

    time_now = datetime.now(tz=timezone.utc)

    with conn.cursor() as curs:
        curs.execute(
            "SELECT image FROM recipe_api_image WHERE is_temporary IS true AND (%s) > expiration_date;",
            (time_now,)
        )
        expired_images = curs.fetchall()

    return expired_images


def delete_expired_from_db(images):

    with conn.cursor() as curs:
        curs.execute(
            "DELETE FROM recipe_api_image WHERE image IN %s;",
            (tuple(map(lambda image: image[0], images)),)
        )

    conn.commit()


if __name__ == "__main__":

    conn = psycopg2.connect(
        database="recipeproject",
        user="projectuser",
        password="rootpassword",
        host="127.0.0.1",
        port="5432"
    )

    expired_images = get_expired_images()

    if expired_images:
        delete_images_from_storage(expired_images)
        delete_expired_from_db(expired_images)
    print(f"{len(expired_images)} images have been deleted on {datetime.now(tz=timezone.utc)}")
