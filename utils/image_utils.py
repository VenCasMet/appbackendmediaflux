LOSSLESS_FORMATS = {
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
    ".gif"
}

LOSSY_FORMATS = {
    ".jpg",
    ".jpeg"
}


def get_compression_mode(src):

    ext = src.suffix.lower()

    if ext in LOSSY_FORMATS:
        return False, "lossy"

    return True, "lossless"