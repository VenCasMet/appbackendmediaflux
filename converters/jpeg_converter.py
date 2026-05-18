from pathlib import Path

from PIL import Image

from converters.base_converter import BaseConverter
from core.settings import FORMAT_CONFIG


class JPEGConverter(BaseConverter):

    def convert(self, job, output_path: Path):

        config = FORMAT_CONFIG["jpeg"]

        with Image.open(job.source_path) as img:

            # =========================
            # PREPARE IMAGE
            # =========================

            img = self.prepare_image(
                img,
                job
            )

            # JPEG requires RGB
            if img.mode != "RGB":

                img = img.convert("RGB")

            # =========================
            # SAVE SETTINGS
            # =========================

            save_kwargs = {

                "format":
                    config["pil_format"],

                "quality":
                    job.quality,

                "optimize":
                    True
            }

            img.save(
                output_path,
                **save_kwargs
            )

        return output_path