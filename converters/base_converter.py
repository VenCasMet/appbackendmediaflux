from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image


class BaseConverter(ABC):

    def prepare_image(self, image: Image.Image):

        if image.mode in ("RGBA", "LA", "P"):
            return image.convert("RGBA")

        if image.mode != "RGB":
            return image.convert("RGB")

        return image

    @abstractmethod
    def convert(self, job, output_path: Path):
        pass