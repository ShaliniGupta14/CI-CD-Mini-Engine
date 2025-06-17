from celery import Celery
from models.database import SessionLocal
from models.schema import Job
import subprocess
import redis
import json

# Set up Redis connection for job status and publishing
redis_client = redis.Redis(host='localhost', port=6379, db=1)
``
# Configure Celery
celery_app = Celery(
    "ci_cd_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

def update_job_status(job_id: int, status: str):
    key = f"job_status:{job_id}"
    redis_client.set(key, status)
    # Publish update to WebSocket listeners
    redis_client.publish("job_updates", json.dumps({job_id: status}))

@celery_app.task(name="tasks.executor.run_job")
def run_job(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()

    if not job:
        update_job_status(job_id, "not_found")
        return f"Job {job_id} not found."

    try:
        # Mark job as running
        job.status = "running"
        db.commit()
        update_job_status(job_id, "running")

        # Execute the job script
        result = subprocess.run(job.script, shell=True, capture_output=True, text=True)

        if result.returncode == 0:
            job.status = "success"
            update_job_status(job_id, "success")
        else:
            job.status = "failed"
            update_job_status(job_id, "failed")

        job.logs = result.stdout + result.stderr
        db.commit()

        return f"Job {job_id} completed."

    except Exception as e:
        job.status = "failed"
        job.logs = str(e)
        db.commit()
        update_job_status(job_id, f"failed: {str(e)}")
        return f"Job {job_id} failed: {e}"
