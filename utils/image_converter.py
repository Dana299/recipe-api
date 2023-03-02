from io import BytesIO

from PIL import Image as PillowImage
from django.core.files.uploadedfile import InMemoryUploadedFile, TemporaryUploadedFile

import sys


class JpegConverter:

    FORMAT = 'JPEG'
    MODE = 'RGB'
    WIDTH = 600

    @classmethod
    def convert(cls, image: TemporaryUploadedFile) -> InMemoryUploadedFile:
        """
        Converts the given image into JPEG format.
        """
        img = PillowImage.open(image)
        width, height = img.size
        new_height = cls.WIDTH * height // width
        img = img.resize((cls.WIDTH, new_height))
        img_io = BytesIO()
        img = img.convert(cls.MODE)
        img.save(img_io, format=cls.FORMAT, quality=100)

        img_io.seek(0)

        img_file = InMemoryUploadedFile(
            file=img_io,
            field_name=None,
            name=f"{image.name.split('.')[0]}.jpeg",
            content_type='image/jpeg',
            size=sys.getsizeof(img_io),
            charset=None
        )

        return img_file