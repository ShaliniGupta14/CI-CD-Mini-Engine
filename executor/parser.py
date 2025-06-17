import yaml

def load_pipeline_yaml(path: str) -> dict:
    """Load the YAML file into a Python dictionary"""
    with open(path, 'r') as f:
        return yaml.safe_load(f)

def get_pipeline_metadata(yaml_data: dict):
    """Extract pipeline name and stages"""
    pipeline = yaml_data.get('pipeline', {})
    name = pipeline.get('name')
    stages = pipeline.get('stages', [])
    return name, stages
