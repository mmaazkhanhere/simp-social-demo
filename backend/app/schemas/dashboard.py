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

