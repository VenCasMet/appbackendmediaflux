from queue import Queue


class QueueManager:

    def __init__(self):

        self.pending_queue = Queue()

        self.completed_jobs = []

        self.failed_jobs = []

    def add_job(self, job):

        job.status = "queued"

        self.pending_queue.put(job)

    def get_next_job(self):

        if not self.pending_queue.empty():

            return self.pending_queue.get()

        return None

    def mark_completed(self, job):

        job.status = "completed"

        self.completed_jobs.append(job)

    def mark_failed(self, job):

        job.status = "failed"

        self.failed_jobs.append(job)

    def has_jobs(self):

        return not self.pending_queue.empty()