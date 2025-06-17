from fastapi import APIRouter, HTTPException
from models.database import SessionLocal
from models.schema import Pipeline, Job
from tasks.executor import run_job
import redis

router = APIRouter()

# Connect to Redis (separate DB to avoid collision with Celery broker/backend)
redis_client = redis.Redis(host="localhost", port=6379, db=1)

@router.post("/pipeline/{pipeline_id}/run")
def run_pipeline(pipeline_id: int):
    db = SessionLocal()
    pipeline = db.query(Pipeline).filter(Pipeline.id == pipeline_id).first()

    if not pipeline:
        db.close()
        raise HTTPException(status_code=404, detail="Pipeline not found.")

    for job in pipeline.jobs:
        redis_client.set(f"job_status:{job.id}", "queued")  # Mark as queued before dispatch
        run_job.delay(job.id)  # Enqueue each job
    db.close()

    return {"message": f"Pipeline {pipeline_id} is being executed."}

@router.get("/jobs/status")
def get_all_job_statuses():
    db = SessionLocal()
    jobs = db.query(Job).all()
    job_statuses = []

    for job in jobs:
        status = redis_client.get(f"job_status:{job.id}")
        decoded_status = status.decode("utf-8") if status else job.status
        job_statuses.append({
            "job_id": job.id,
            "name": job.name,
            "status": decoded_status,
            "script": job.script,
        })

    db.close()
    return {"jobs": job_statuses}
