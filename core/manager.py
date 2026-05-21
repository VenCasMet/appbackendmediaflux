import gc
import time

from PIL import Image
from pathlib import Path

from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed
)
from utils.target_size_optimizer import (
    TargetSizeOptimizer
)
from core.benchmark_engine import BenchmarkEngine
from core.queue_manager import QueueManager

from converters.webp_converter import WebPConverter
from converters.jpeg_converter import JPEGConverter
from converters.png_converter import PNGConverter
from converters.avif_converter import AVIFConverter

from utils.stats import calculate_reduction
from utils.progress_tracker import ProgressTracker
from utils.optimizer import OptimizationAnalyzer
from utils.image_analyzer import ImageAnalyzer
from utils.quality_analyzer import QualityAnalyzer
from utils.comparison_engine import ComparisonEngine
from utils.quality_optimizer import QualityOptimizer
from utils.heatmap_generator import HeatmapGenerator
from utils.comparison_generator import ComparisonGenerator


class ConversionManager:

    def __init__(self, workers=2):

        # REDUCED WORKERS
        # VERY IMPORTANT FOR MEMORY SAFETY
        self.workers = workers

        self.queue_manager = QueueManager()

        self.benchmark_engine = BenchmarkEngine(self)

        self.converters = {
            "webp": WebPConverter(),
            "jpeg": JPEGConverter(),
            "png": PNGConverter(),
            "avif": AVIFConverter()
        }

        self.comparison_engine = ComparisonEngine()

    def get_converter(self, output_format):

        converter = self.converters.get(output_format)

        if not converter:
            raise ValueError(
                f"Unsupported format: {output_format}"
            )

        return converter

    def cleanup_memory(self):

        gc.collect()

    def process_job(self, job, progress_callback=None):

        converter = self.get_converter(
            job.output_format
        )

        try:

            start_time = time.time()

            job.status = "processing"

            # =========================
            # STAGE 1 - ANALYZE
            # =========================

            ProgressTracker.update(
                job,
                10,
                "loading"
            )
            if progress_callback:
                progress_callback(job)

            job.image_analysis = (
                ImageAnalyzer.analyze(
                    job.source_path
                )
            )

            job.original_size = (
                job.source_path.stat().st_size
            )

            # =========================
            # STAGE 2 - PREPARE
            # =========================

            ProgressTracker.update(
                job,
                25,
                "preparing"
            )
            if progress_callback:
                progress_callback(job)

            job.image_type = (
                QualityOptimizer.detect_image_type(
                    job.source_path
                )
            )

            # =========================
            # STAGE 3 - CONVERT
            # =========================

            ProgressTracker.update(
                job,
                50,
                "converting"
            )
            if progress_callback:
                progress_callback(job)

            if job.target_size_enabled:

                TargetSizeOptimizer.optimize_quality(

                    converter=converter,

                    job=job,

                    target_size_kb=job.target_size_kb
                )

            else:

                converter.convert(
                    job,
                    job.output_path
                )

            # =========================
            # STAGE 4 - ANALYZE RESULT
            # =========================

            ProgressTracker.update(
                job,
                70,
                "analyzing"
            )
            if progress_callback:
                progress_callback(job)

            job.converted_size = (
                job.output_path.stat().st_size
            )

            reduction, percent = (
                calculate_reduction(
                    job.original_size,
                    job.converted_size
                )
            )

            job.reduction_bytes = reduction
            job.reduction_percent = percent

            job.ssim_score = (
                QualityAnalyzer.calculate_ssim(
                    job.source_path,
                    job.output_path
                )
            )

            job.optimization_result = (
                OptimizationAnalyzer.analyze(job)
            )

            with Image.open(job.output_path) as img:

                job.resolution = (
                    f"{img.width}x{img.height}"
                )

            # =========================
            # STAGE 5 - HEATMAP
            # =========================

            ProgressTracker.update(
                job,
                85,
                "heatmap"
            )
            if progress_callback:
                progress_callback(job)

            heatmap_output = (
                job.output_path.parent /
                f"{job.source_path.stem}_heatmap.png"
            )

            HeatmapGenerator.generate(
                job.source_path,
                job.output_path,
                heatmap_output
            )

            job.heatmap_path = str(
                heatmap_output
            )

            # =========================
            # STAGE 6 - COMPARISON
            # =========================

            ProgressTracker.update(
                job,
                92,
                "comparison"
            )
            if progress_callback:
                progress_callback(job)

            comparison_output = (
                job.output_path.parent /
                f"{job.source_path.stem}_compare.jpg"
            )

            ComparisonGenerator.generate(
                job.source_path,
                job.output_path,
                comparison_output
            )

            job.comparison_path = str(
                comparison_output
            )

            # =========================
            # FINALIZE
            # =========================

            job.processing_time = round(
                time.time() - start_time,
                2
            )

            job.status = "completed"

            ProgressTracker.update(
                job,
                100,
                "completed"
            )
            if progress_callback:
                progress_callback(job)

        except Exception as e:

            job.status = "failed"

            job.error = str(e)

            ProgressTracker.update(
                job,
                0,
                "failed"
            )
            if progress_callback:
                progress_callback(job)
        finally:

            # VERY IMPORTANT
            self.cleanup_memory()

        return job

    def process_batch(self, jobs):

        results = []

        # =========================
        # ADD TO QUEUE
        # =========================

        for job in jobs:

            self.queue_manager.add_job(job)

        queued_jobs = []

        while self.queue_manager.has_jobs():

            next_job = (
                self.queue_manager.get_next_job()
            )

            if next_job:

                queued_jobs.append(next_job)

        # =========================
        # SAFE THREAD PROCESSING
        # =========================

        with ThreadPoolExecutor(
            max_workers=self.workers
        ) as executor:

            future_map = {

                executor.submit(
                    self.process_job,
                    job
                ): job

                for job in queued_jobs
            }

            for future in as_completed(future_map):

                job_result = future.result()

                if (
                    job_result.status
                    == "completed"
                ):

                    self.queue_manager.mark_completed(
                        job_result
                    )

                else:

                    self.queue_manager.mark_failed(
                        job_result
                    )

                results.append(job_result)

                # EXTRA CLEANUP
                self.cleanup_memory()

        return results