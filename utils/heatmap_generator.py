from pathlib import Path
import matplotlib

matplotlib.use("Agg")
import numpy as np
import matplotlib.pyplot as plt

from PIL import Image
from PIL import ImageChops


class HeatmapGenerator:

    @staticmethod
    def generate(
        original_path,
        compressed_path,
        output_path
    ):

        # LOAD IMAGES
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

        # DIFFERENCE IMAGE
        diff = ImageChops.difference(
            original,
            compressed
        )

        # NUMPY ARRAY
        diff_array = np.array(diff)

        # HEAT INTENSITY
        heatmap = diff_array.mean(axis=2)

        # CREATE OUTPUT FOLDER
        output_folder = (
            Path("outputs")
            / "heatmaps"
        )

        output_folder.mkdir(
            parents=True,
            exist_ok=True
        )

        # CREATE FIGURE
        fig, ax = plt.subplots(
            figsize=(6, 6)
        )

        ax.imshow(
            heatmap,
            cmap="hot"
        )

        ax.axis("off")

        fig.savefig(
            str(output_path)
        )

        plt.clf()
        plt.close("all")