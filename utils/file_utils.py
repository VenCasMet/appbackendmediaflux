import os
from pathlib import Path

SUPPORTED_FORMATS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".tiff",
    ".tif",
    ".gif",
    ".webp",
    ".avif"
}


def human_size(n_bytes: int) -> str:

    for unit in ("B", "KB", "MB", "GB"):

        if n_bytes < 1024:
            return f"{n_bytes:.1f} {unit}"

        n_bytes /= 1024

    return f"{n_bytes:.1f} TB"


def clean_filename(name: str) -> str:

    name = name.replace(" ", "_")

    return name[:30]


def collect_images(root: Path):

    images = []

    for dirpath, _, filenames in os.walk(root):

        for fn in filenames:

            if Path(fn).suffix.lower() in SUPPORTED_FORMATS:
                images.append(Path(dirpath) / fn)

    return sorted(images)