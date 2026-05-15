class ProgressTracker:

    @staticmethod
    def update(job, progress, stage):

        job.progress = progress

        job.current_stage = stage