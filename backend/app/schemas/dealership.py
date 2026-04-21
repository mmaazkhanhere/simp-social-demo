from pydantic import BaseModel


class DealershipRead(BaseModel):
    id: int
    name: str
    slug: str
    language_default: str

    model_config = {"from_attributes": True}

