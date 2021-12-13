from datetime import datetime
from pydantic import BaseModel
from bson import Binary
class Plant(BaseModel):
    image_url: str
    status: str
    created_at: datetime
