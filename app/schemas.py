from datetime import datetime
from typing import Optional
from fastapi import HTTPException
from pydantic import BaseModel, ValidationError, validator

class GetStock(BaseModel):
    id : int
    code : int
    name : str
    open : float
    close : float
    high : float
    low : float
    date : datetime

class EnterName(BaseModel):
    name : str
    

class AddToFav(BaseModel):
    name : str
    code : int

class StockHistory(BaseModel):
    open : float