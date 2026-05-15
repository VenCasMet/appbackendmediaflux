from pathlib import Path
import argparse

from reports.report_generator import ReportGenerator
from core.job import ConversionJob
from core.manager import ConversionManager
from core.settings import FORMAT_CONFIG
from utils.file_utils import collect_images, clean_filename
from utils.logger import logger


def parse_args():

    parser = argparse.ArgumentParser(
        description="Universal Image Conversion Engine"
    )

    parser.add_argument(
        "--format",
        help="Target output format"
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=85,
        help="Compression quality"
    )

    parser.add_argument(
        "--method",
        type=int,
        default=6,
        help="Compression method"
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically choose best format"
    )

    return parser.parse_args()


def main():

    args = parse_args()

    output_format = (
        args.format.lower()
        if args.format
        else None
    )

    if not args.auto:

        if output_format not in FORMAT_CONFIG:

            logger.error(
                f"Unsupported format: {output_format}"
            )

            return

    input_path = Path("sample_images")

    output_dir = Path("outputs")

    output_dir.mkdir(exist_ok=True)

    images = collect_images(input_path)

    logger.info(f"Found {len(images)} images")

    manager = ConversionManager()

    jobs = []

           # CREATE JOBS
    for img in images:

        original_ext = img.suffix.replace(".", "")

        # DEFAULT FORMAT
        selected_format = output_format

        # AUTO MODE
        if args.auto:

            benchmark_result = (
                manager.benchmark_engine.benchmark(img)
            )

            # BENCHMARK FAILED
            if not benchmark_result:

                logger.warning(
                    f"{img.name} | Benchmark failed"
                )

                continue

            best = benchmark_result["best"]

            # INVALID RESULT
            if not best:

                logger.warning(
                    f"{img.name} | No valid optimization"
                )

                continue

            # KEEP ORIGINAL
            if best.reduction_percent < 10:

                logger.info(
                    f"{img.name} | KEEP ORIGINAL"
                )

                continue

            # SAFE FORMAT FALLBACK
            selected_format = (
                best.output_format
                if best.output_format
                else "webp"
            )

            logger.info(
                f"{img.name} | AUTO selected: "
                f"{selected_format.upper()}"
            )

        # DYNAMIC EXTENSION
        extension = FORMAT_CONFIG[
            selected_format
        ]["extension"]

        output_name = (
            clean_filename(img.stem)
            + "_from_"
            + original_ext
            + extension
        )

        output_path = output_dir / output_name

        job = ConversionJob(
            source_path=img,
            output_format=selected_format,
            quality=args.quality,
            method=args.method,
            output_path=output_path
        )

        jobs.append(job)

    # PROCESS JOBS
    results = manager.process_batch(jobs)

    # DISPLAY RESULTS
    for result in results:

        if result.status == "completed":

            recommendation = (
                result.benchmark_recommendation.upper()
            )

            logger.info(
                f"[{result.current_stage.upper()}] "
                f"{result.source_path.name} | "
                f"{result.progress}% | "
                f"{round(result.original_size / 1024, 2)} KB -> "
                f"{round(result.converted_size / 1024, 2)} KB | "
                f"Saved {result.reduction_percent}% | "
                f"SSIM {result.ssim_score} | "
                f"Q {result.quality} | "
                f"{result.optimization_result['recommendation']} | "
                f"Recommended: {recommendation} | "
                f"Heatmap: GENERATED | "
                f"Comparison: GENERATED | "
                f"{result.processing_time}s"
            )

        else:

            logger.error(
                f"[FAILED] "
                f"{result.source_path.name} | "
                f"{result.error}"
            )

    # GENERATE REPORT
    report_path = ReportGenerator.generate(results)

    logger.info(f"Report generated: {report_path}")

    # QUEUE SUMMARY
    logger.info(
        f"Completed Jobs: "
        f"{len(manager.queue_manager.completed_jobs)}"
    )

    logger.info(
        f"Failed Jobs: "
        f"{len(manager.queue_manager.failed_jobs)}"
    )

if __name__ == "__main__":
    main()