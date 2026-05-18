from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConversionJob:

    # =========================
    # REQUIRED FIELDS
    # =========================

    source_path: Path

    output_format: str

    quality: int

    method: int

    # =========================
    # TARGET SIZE SETTINGS
    # =========================

    target_size_kb: int = 0

    target_size_enabled: bool = False

    # =========================
    # RESIZE SETTINGS
    # =========================

    resize_enabled: bool = False

    resize_width: int = 0

    resize_height: int = 0

    keep_aspect_ratio: bool = True

    # =========================
    # GENERAL OPTIONS
    # =========================

    overwrite: bool = False

    # =========================
    # JOB STATUS
    # =========================

    status: str = "queued"

    progress: int = 0

    error: str = ""

    current_stage: str = "queued"

    eta: float = 0

    # =========================
    # FILE OUTPUT
    # =========================

    output_path: Path = None

    # =========================
    # SIZE + PERFORMANCE
    # =========================

    original_size: int = 0

    converted_size: int = 0

    reduction_bytes: int = 0

    reduction_percent: float = 0

    processing_time: float = 0

    resolution: str = ""

    # =========================
    # ANALYSIS
    # =========================

    optimization_result: dict = None

    image_analysis: dict = None

    ssim_score: float = 0

    benchmark_recommendation: str = ""

    is_benchmark: bool = False

    keep_original: bool = False

    image_type: str = ""

    # =========================
    # GENERATED ASSETS
    # =========================

    heatmap_path: str = ""

    comparison_path: str = ""