from asyncio import futures
import time

from PIL import Image
from pathlib import Path
from core import job
from core import benchmark_engine
from core.benchmark_engine import BenchmarkEngine
from utils.stats import calculate_reduction
from concurrent.futures import ThreadPoolExecutor, as_completed
from core.queue_manager import QueueManager
from converters.webp_converter import WebPConverter
from converters.jpeg_converter import JPEGConverter
from converters.png_converter import PNGConverter
from converters.avif_converter import AVIFConverter
from utils.progress_tracker import ProgressTracker
from utils.optimizer import OptimizationAnalyzer
from utils.image_analyzer import ImageAnalyzer
from utils.quality_analyzer import QualityAnalyzer
from utils.comparison_engine import ComparisonEngine
from utils.quality_optimizer import (QualityOptimizer)
from utils.heatmap_generator import (HeatmapGenerator)
from utils.comparison_generator import (ComparisonGenerator)

class ConversionManager:

    def __init__(self, workers=4):

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
            raise ValueError(f"Unsupported format: {output_format}")

        return converter

    def process_job(self, job):

        converter = self.get_converter(job.output_format)

        try:

            start_time = time.time()

            job.status = "processing"

            job.image_analysis = (
                ImageAnalyzer.analyze(job.source_path)
            )

            # if not job.is_benchmark:

            #     from core.benchmark_engine import BenchmarkEngine

            #     benchmark_engine = BenchmarkEngine(self)

            #     benchmark_result = benchmark_engine.benchmark(
            #         job.source_path
            #     )

            #     if benchmark_result:

            #         best = benchmark_result["best"]

            #         job.benchmark_recommendation = (
            #             best.output_format
            #         )

            #         # TRANSFER KEEP-ORIGINAL DECISION
            #         job.keep_original = best.keep_original

        # STAGE 1
            ProgressTracker.update(
                job,
                10,
                "loading"
            )

            job.original_size = job.source_path.stat().st_size

        # STAGE 2
            ProgressTracker.update(
                job,
                30,
                "preparing"
            )

            time.sleep(0.05)

        # STAGE 3
            ProgressTracker.update(
                job,
                60,
                "converting"
            )

            job.image_type = (
                QualityOptimizer.detect_image_type(
                    job.source_path
                )
            )

            converter.convert(job, job.output_path)

        # STAGE 4
            ProgressTracker.update(
                job,
                85,
                "analyzing"
            )

            job.converted_size = job.output_path.stat().st_size

            reduction, percent = calculate_reduction(
                job.original_size,
                job.converted_size
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

                job.resolution = f"{img.width}x{img.height}"

        # STAGE 5
            ProgressTracker.update(
                job,
                95,
                "finalizing"
            )

            job.processing_time = round(
                time.time() - start_time,
                2
            )

            heatmap_output = (
                Path("outputs")
                / "heatmaps"
                / f"{job.source_path.stem}_heatmap.png"
            )

            HeatmapGenerator.generate(
                job.source_path,
                job.output_path,
                heatmap_output
            )

            job.heatmap_path = str(
                heatmap_output
            )

            comparison_output = (
                Path("outputs")
                / "comparisons"
                / f"{job.source_path.stem}_compare.jpg"
            )

            ComparisonGenerator.generate(
                job.source_path,
                job.output_path,
                comparison_output
            )

            job.comparison_path = str(
                comparison_output
            )

            job.status = "completed"

            ProgressTracker.update(
                job,
                100,
                "completed"
            )

        except Exception as e:

            job.status = "failed"

            job.error = str(e)

            ProgressTracker.update(
                job,
                0,
                "failed"
            )

        return job

    def process_batch(self, jobs):

        results = []

    # ADD JOBS TO QUEUE
        for job in jobs:

            self.queue_manager.add_job(job)

        queued_jobs = []

    # EXTRACT QUEUE SAFELY
        while self.queue_manager.has_jobs():

            job = self.queue_manager.get_next_job()

            if job:

                queued_jobs.append(job)

    # PROCESS THREADS
        with ThreadPoolExecutor(max_workers=self.workers) as executor:

            futures = [
                executor.submit(self.process_job, job)
                for job in queued_jobs
            ]

            for future in as_completed(futures):

                job_result = future.result()

                if job_result.status == "completed":
                
                    self.queue_manager.mark_completed(job_result)

                else:

                    self.queue_manager.mark_failed(job_result)

                results.append(job_result)

        return results