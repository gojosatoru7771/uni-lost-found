from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ItemCreate(BaseModel):
    type: str
    category: str
    title: str
    description: str
    location: str
    time: datetime


class Item(ItemCreate):
    id: int
    is_resolved: bool = False
    claims: List[dict] = []