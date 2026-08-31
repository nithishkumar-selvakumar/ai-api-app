from typing import Optional
from pydantic import BaseModel, EmailStr


class EmailSummary(BaseModel):
    short_description: str
    description: str


class EmailContent(BaseModel):
    subject: str
    summary: EmailSummary


class Priority(BaseModel):
    value: int
    label: str


class RequestedFor(BaseModel):
    name: str
    email: EmailStr
    country: str


class Ticket(BaseModel):
    email: EmailContent
    assignment_group: str
    state: str
    priority: Priority
    requested_for: RequestedFor
    service: str
    id: str
    service_offering: str
    base_item: Optional[str] = None
    category: str