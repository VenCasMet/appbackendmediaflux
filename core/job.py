from dataclasses import dataclass
from pathlib import Path


@dataclass
class ConversionJob:

    source_path: Path

    output_format: str

    quality: int

    method: int

    overwrite: bool = False

    status: str = "queued"

    progress: int = 0

    error: str = ""

    output_path: Path = None

    original_size: int = 0

    converted_size: int = 0

    reduction_bytes: int = 0

    reduction_percent: float = 0

    processing_time: float = 0

    resolution: str = ""

    current_stage: str = "queued"

    eta: float = 0

    optimization_result: dict = None

    image_analysis: dict = None

    ssim_score: float = 0

    benchmark_recommendation: str = ""

    is_benchmark: bool = False

    keep_original: bool = False

    image_type: str = ""

    heatmap_path: str = ""

    comparison_path: str = ""