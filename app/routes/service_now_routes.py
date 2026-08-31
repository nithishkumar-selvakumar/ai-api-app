from fastapi import APIRouter

from app.controllers.service_now_controller import insert_service_now_incident
from app.models.service_now_model import Ticket

router = APIRouter(
    prefix="/api/service-now",
    tags=["service-now"],
)

@router.post("/ticket/{project_name}")
async def investigate_ticket(project_name: str, ticket: Ticket):
    return insert_service_now_incident(
        project_name=project_name,
        incident_data=ticket,
    )