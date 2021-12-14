from pydantic import BaseModel
from datetime import datetime
class Envi(BaseModel): 
    temp: int
    humid: int
    time: datetime