from typing import Optional, Union

from pydantic import BaseModel


class PrecisionField(BaseModel):
    amount: Union[float, int]
    price: Union[float, int]


class LimitField(BaseModel):
    min: Optional[float]
    max: Optional[float]


class LimitsField(BaseModel):
    amount: LimitField
    price: LimitField
    cost: LimitField


class CurrencyInfo(BaseModel):
    id: str
    symbol: str
    base: str
    quote: str
    active: bool
    precision: PrecisionField
    taker: Optional[float]
    maker: Optional[float]
    type: Optional[str]
    spot: Optional[bool]
    swap: Optional[bool]
    future: Optional[bool]
    option: Optional[bool]
    linear: Optional[bool]
    inverse: Optional[bool]
    limits: LimitsField
    info: dict
