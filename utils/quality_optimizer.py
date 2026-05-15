from PIL import Image


class QualityOptimizer:

    @staticmethod
    def detect_image_type(image_path):

        with Image.open(image_path) as img:

            width, height = img.size

            # TRANSPARENCY
            has_alpha = (
                img.mode in ("RGBA", "LA")
            )

            # SIMPLE HEURISTICS
            if has_alpha:

                return "transparent"

            # SMALL IMAGE = UI / SCREENSHOT
            if width < 800 and height < 800:

                return "ui"

            # LARGE IMAGE = PHOTO
            return "photo"

    @staticmethod
    def recommend_quality(image_type):

        quality_map = {

            "photo": 78,

            "ui": 92,

            "transparent": 95
        }

        return quality_map.get(
            image_type,
            85
        )