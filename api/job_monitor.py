from fastapi import APIRouter, HTTPException
from models.database import SessionLocal
from models.schema import Job
from tasks.state import job_statuses

router = APIRouter()

@router.get("/jobs/{job_id}/logs")
def get_job_logs(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "job_id": job.id,
        "name": job.name,
        "logs": job.logs or "No logs available"
    }

@router.get("/jobs/{job_id}/status")
def get_job_status(job_id: int):
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    db.close()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # Prefer in-memory live status
    live_status = job_statuses.get(job_id, job.status)
    return {
        "job_id": job.id,
        "name": job.name,
        "status": live_status
    }
