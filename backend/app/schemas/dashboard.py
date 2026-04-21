from pydantic import BaseModel


class SummaryMetric(BaseModel):
    label: str
    value: int


class DashboardSummaryResponse(BaseModel):
    metrics: list[SummaryMetric]


class DealershipRollup(BaseModel):
    dealership_id: int
    dealership_name: str
    conversations: int
    leads: int
    users: int


class DealershipDashboardResponse(BaseModel):
    dealership_id: int
    dealership_name: str
    metrics: list[SummaryMetric]


class LeadRow(BaseModel):
    name: str
    phone: str
    employment_status: str
    monthly_income_range: str
    down_payment_range: str
    timeline: str
    intent_score: str


class ConversationRow(BaseModel):
    id: int
    status: str
    stage: str
    language: str


class NotificationRow(BaseModel):
    id: int
    event_type: str
    delivery_status: str
    sent_at: str


class UserRow(BaseModel):
    name: str
    phone: str
    employment_status: str
    monthly_income_range: str
    down_payment_range: str
    timeline: str
    intent_score: str
