import numpy as np

from PIL import Image

from skimage.metrics import structural_similarity as ssim


class QualityAnalyzer:

    @staticmethod
    def calculate_ssim(original_path, compressed_path):

        original = Image.open(original_path).convert("RGB")

        compressed = Image.open(compressed_path).convert("RGB")

        # Resize if dimensions mismatch
        if original.size != compressed.size:

            compressed = compressed.resize(original.size)

        original_np = np.array(original)

        compressed_np = np.array(compressed)

        score = ssim(
            original_np,
            compressed_np,
            channel_axis=2
        )

        return round(score, 4)