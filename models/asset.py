from pydantic import BaseModel
from typing import Optional

class AssetBase(BaseModel):
    name: str
    symbol: str
    type: str
    price: float

class AssetCreate(AssetBase):
    pass

class AssetResponse(AssetBase):
    id: int

class Asset(AssetBase):
    id: int
