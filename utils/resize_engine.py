from PIL import Image


class ResizeEngine:

    @staticmethod
    def resize_image(
        image,
        width,
        height,
        keep_aspect_ratio=True
    ):

        if keep_aspect_ratio:

            image.thumbnail(
                (width, height)
            )

            return image

        return image.resize(
            (width, height)
        )