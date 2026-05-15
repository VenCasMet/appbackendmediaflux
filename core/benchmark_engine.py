from utils.format_tester import FormatTester


class BenchmarkEngine:

    def __init__(self, manager):

        self.manager = manager

        self.test_formats = [
            "webp",
            "avif",
            "png",
            "jpeg"
        ]

    def benchmark(self, source_path):

        benchmark_jobs = []

        # CREATE TEST JOBS
        for format_name in self.test_formats:

            job = FormatTester.build_test_job(
                source_path,
                format_name
            )

            benchmark_jobs.append(job)

        # PROCESS TESTS
        results = self.manager.process_batch(
            benchmark_jobs
        )

        valid_results = [

            r for r in results

            if r.status == "completed"
        ]

        if not valid_results:

            return None

        # SCORE + RANK
        ranked_results = sorted(

            valid_results,

            key=lambda r:
                self.manager
                .comparison_engine
                .calculate_score(r),

            reverse=True
        )

        best = ranked_results[0]

        return {
            "best": best,
            "results": valid_results,
            "ranked": ranked_results
        }