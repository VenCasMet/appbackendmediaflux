from pathlib import Path

from PIL import Image

from converters.base_converter import BaseConverter
from core.settings import FORMAT_CONFIG


class WebPConverter(BaseConverter):

    def convert(self, job, output_path: Path):

        config = FORMAT_CONFIG["webp"]

        with Image.open(job.source_path) as img:

            img = self.prepare_image(
    img,
    job
)

            save_kwargs = {
                "format": config["pil_format"],
                "method": job.method,
                "quality": job.quality
            }

            img.save(output_path, **save_kwargs)

        return output_path