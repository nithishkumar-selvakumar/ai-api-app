
import json
from pathlib import Path

from app.models.service_now_model import Ticket

UPLOAD_ROOT = Path("uploaded-docs")


def save_incident(project_name: str, incident_data: Ticket):
    project_dir = UPLOAD_ROOT / project_name
    project_dir.mkdir(parents=True, exist_ok=True)

    incident_file = project_dir / "service-now-insident.json"

    if incident_file.exists():
        try:
            with open(incident_file, "r", encoding="utf-8") as f:
                incidents = json.load(f)

                if not isinstance(incidents, list):
                    incidents = [incidents]

        except json.JSONDecodeError:
            incidents = []
    else:
        incidents = []

    # Convert Pydantic Ticket model to a JSON-serializable dictionary
    incidents.append(incident_data.model_dump(mode="json"))

    with open(incident_file, "w", encoding="utf-8") as f:
        json.dump(incidents, f, indent=4)

    return incident_data

