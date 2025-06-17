from tasks.worker import run_job  # ✅ safe now

def execute_pipeline_jobs(jobs):
    for job in jobs:
        run_job.delay(job.id)
