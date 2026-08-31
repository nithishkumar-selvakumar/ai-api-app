
from app.models.service_now_model import Ticket
from app.services.service_now_service import save_incident


def insert_service_now_incident(project_name: str, incident_data: Ticket):
    return save_incident(
        project_name=project_name,
        incident_data=incident_data,
    )