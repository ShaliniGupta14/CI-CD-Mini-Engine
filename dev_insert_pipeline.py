from executor.parser import load_pipeline_yaml, get_pipeline_metadata
from models.database import SessionLocal
from models.schema import Pipeline, Job

pipeline_data = load_pipeline_yaml("pipelines/sample_pipeline.yml")
name, stages = get_pipeline_metadata(pipeline_data)

db = SessionLocal()

# Create pipeline entry
pipeline = Pipeline(name=name)
db.add(pipeline)
db.commit()
db.refresh(pipeline)

# Create job entries
for stage in stages:
    job = Job(
        name=stage["name"],
        script=stage["script"],
        status="pending",
        pipeline_id=pipeline.id
    )
    db.add(job)

db.commit()
print("Pipeline and jobs inserted.")
