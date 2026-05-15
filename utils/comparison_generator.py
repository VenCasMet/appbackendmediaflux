from pathlib import Path

from PIL import Image
from PIL import ImageDraw


class ComparisonGenerator:

    @staticmethod
    def generate(
        original_path,
        compressed_path,
        output_path
    ):

        original = (
            Image.open(original_path)
            .convert("RGB")
        )

        compressed = (
            Image.open(compressed_path)
            .convert("RGB")
        )

        # MATCH SIZE
        compressed = compressed.resize(
            original.size
        )

        width, height = original.size

        # CREATE SIDE-BY-SIDE CANVAS
        canvas = Image.new(
            "RGB",
            (width * 2, height)
        )

        # PASTE IMAGES
        canvas.paste(original, (0, 0))

        canvas.paste(compressed, (width, 0))

        # LABELS
        draw = ImageDraw.Draw(canvas)

        draw.text(
            (20, 20),
            "ORIGINAL",
            fill=(255, 255, 255)
        )

        draw.text(
            (width + 20, 20),
            "COMPRESSED",
            fill=(255, 255, 255)
        )

        # CREATE FOLDER
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        # SAVE
        canvas.save(output_path)