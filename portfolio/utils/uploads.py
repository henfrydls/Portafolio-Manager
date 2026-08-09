"""Upload-path helpers."""
import uuid
from pathlib import Path

from django.utils.deconstruct import deconstructible


@deconstructible
class UUIDUploadTo:
    """upload_to callable that renames uploads to a UUID, keeping the extension.

    Prevents original filenames (which may carry sensitive information)
    from reaching public media URLs, and avoids name collisions.
    """

    def __init__(self, subdir):
        self.subdir = subdir.strip('/')

    def __call__(self, instance, filename):
        ext = Path(filename).suffix.lower()
        return f'{self.subdir}/{uuid.uuid4().hex}{ext}'

    def __eq__(self, other):
        return isinstance(other, UUIDUploadTo) and self.subdir == other.subdir
