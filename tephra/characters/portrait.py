"""Character portraits: uploads are checked by decoding them with Pillow and re-encoded (max 600 px, no EXIF)."""
import io
import uuid

from django.core.files.base import ContentFile
from PIL import Image, ImageOps

from rules.lang import gettext as _

MAX_BYTES = 2 * 1024 * 1024
MAX_PX = 600
FORMATS = {"JPEG", "PNG", "WEBP"}


class PortraitError(ValueError):
    pass


def process(upload):
    """Uploaded file -> ContentFile (WebP) or PortraitError. The original bytes are never stored."""
    if upload.size > MAX_BYTES:
        raise PortraitError(_("The portrait is larger than 2 MB."))
    try:
        data = upload.read()
        with Image.open(io.BytesIO(data)) as img:
            if img.format not in FORMATS:
                raise PortraitError(_("Only JPEG, PNG or WebP images can be used as portrait."))
            img.verify()
        with Image.open(io.BytesIO(data)) as img:  # verify() leaves the image unusable: decode a fresh copy
            img = ImageOps.exif_transpose(img)
            img.thumbnail((MAX_PX, MAX_PX))
            out = io.BytesIO()
            img.convert("RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB").save(out, "WEBP", quality=85)
    except PortraitError:
        raise
    except Exception:  # truncated/corrupt files, decompression bombs, anything Pillow refuses
        raise PortraitError(_("This file is not a readable image."))
    return ContentFile(out.getvalue(), name=f"{uuid.uuid4().hex}.webp")
