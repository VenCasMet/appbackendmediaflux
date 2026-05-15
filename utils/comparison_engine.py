class ComparisonEngine:

    @staticmethod
    def calculate_score(job):

        quality_weight = job.ssim_score * 100

        size_weight = job.reduction_percent

        if size_weight < 0:

            size_weight *= 3

        final_score = (
            quality_weight * 0.7
            +
            size_weight * 0.3
        )

        return final_score

    @staticmethod
    def should_keep_original(best_job):

        # NEGATIVE SAVINGS
        if best_job.reduction_percent <= 0:

            return True

        # TOO LITTLE BENEFIT
        if best_job.reduction_percent < 10:

            return True

        return False

    @staticmethod
    def choose_best(results):

        valid_results = [

            r for r in results

            if r.status == "completed"
        ]

        if not valid_results:

            return None

        ranked_results = sorted(

            valid_results,

            key=lambda r:
                ComparisonEngine.calculate_score(r),

            reverse=True
        )

        best = ranked_results[0]

        # KEEP ORIGINAL CHECK
        if ComparisonEngine.should_keep_original(best):

            best.keep_original = True

        return best