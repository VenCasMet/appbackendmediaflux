from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image, ImageOps
from utils.resize_engine import ResizeEngine


class BaseConverter(ABC):

    def prepare_image(self, image: Image.Image, job=None):
        image = ImageOps.exif_transpose(image)

        # =========================
        # COLOR MODE FIXES
        # =========================

        if image.mode in ("RGBA", "LA", "P"):

            image = image.convert("RGBA")

        elif image.mode != "RGB":

            image = image.convert("RGB")

        # =========================
        # RESIZE SUPPORT
        # =========================

        if (

            job
            and
            job.resize_enabled
            and
            job.resize_width > 0
            and
            job.resize_height > 0
        ):

            image = ResizeEngine.resize_image(

                image=image,

                width=job.resize_width,

                height=job.resize_height,

                keep_aspect_ratio=(
                    job.keep_aspect_ratio
                )
            )

        return image

    @abstractmethod
    def convert(self, job, output_path: Path):

        pass