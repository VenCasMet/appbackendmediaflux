from pathlib import Path


class TargetSizeOptimizer:

    @staticmethod
    def optimize_quality(
        converter,
        job,
        target_size_kb,
        min_quality=10,
        max_quality=95
    ):

        best_quality = job.quality

        best_size = None

        low = min_quality
        high = max_quality

        while low <= high:

            mid_quality = (
                low + high
            ) // 2

            job.quality = mid_quality

            converter.convert(
                job,
                job.output_path
            )

            current_size_kb = (
                job.output_path
                .stat()
                .st_size
                / 1024
            )

            # VALID RESULT
            if current_size_kb <= target_size_kb:

                best_quality = mid_quality

                best_size = current_size_kb

                low = mid_quality + 1

            else:

                high = mid_quality - 1

        # FINAL BEST QUALITY
        job.quality = best_quality

        converter.convert(
            job,
            job.output_path
        )

        return {
            "quality": best_quality,
            "size_kb": best_size
        }