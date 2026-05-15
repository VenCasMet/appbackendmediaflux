from PIL import Image


class ImageAnalyzer:

    @staticmethod
    def analyze(image_path):

        analysis = {

            "has_transparency": False,

            "mode": "",

            "width": 0,

            "height": 0,

            "recommended_format": "webp"
        }

        with Image.open(image_path) as img:

            analysis["mode"] = img.mode

            analysis["width"] = img.width

            analysis["height"] = img.height

            # Detect transparency
            if img.mode in ("RGBA", "LA"):

                analysis["has_transparency"] = True

            # Smart recommendation logic
            if analysis["has_transparency"]:

                analysis["recommended_format"] = "png"

            elif img.width > 1500:

                analysis["recommended_format"] = "avif"

            else:

                analysis["recommended_format"] = "webp"

        return analysis