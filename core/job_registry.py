class JobRegistry:

    def __init__(self):

        self.jobs = {}

    def create_job(self, job_id):

        self.jobs[job_id] = {
            "status": "queued",
            "progress": 0,
            "results": [],
            "total_files": 0,
            "processed_files": 0,
            "failed_files": 0
        }

    def update_job(
        self,
        job_id,
        data
    ):

        if job_id in self.jobs:

            self.jobs[job_id].update(data)

    def get_job(self, job_id):

        return self.jobs.get(job_id)