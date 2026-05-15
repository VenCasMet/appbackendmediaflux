class OptimizationAnalyzer:

    @staticmethod
    def analyze(job):

        if job.reduction_percent < 0:

            return {
                "success": False,
                "recommendation":
                    "Conversion increased filesize"
            }

        if job.reduction_percent < 10:

            return {
                "success": False,
                "recommendation":
                    "Low optimization benefit"
            }

        return {
            "success": True,
            "recommendation":
                "Good optimization"
        }