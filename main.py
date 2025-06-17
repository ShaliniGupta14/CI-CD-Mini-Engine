from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from models.database import SessionLocal
from models.schema import Job
from api.pipeline_trigger import router as pipeline_router
from api.job_monitor import router as monitor_router  
from fastapi import WebSocket
import asyncio
from tasks.state import job_statuses  # assuming this dict is updated in worker.py


app = FastAPI(title="CI/CD Pipeline Simulator")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def on_startup():
    from models.database import init_db
    init_db()

app.include_router(pipeline_router)
app.include_router(monitor_router)

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request):
    db = SessionLocal()
    jobs = db.query(Job).all()
    db.close()
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": jobs})

@app.websocket("/ws/jobs")
async def websocket_job_status(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(job_statuses)
            await asyncio.sleep(2)  # Send updates every 2 seconds
    except Exception as e:
        print(f"WebSocket error: {e}")
