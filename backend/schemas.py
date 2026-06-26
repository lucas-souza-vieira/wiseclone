from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None
    country: Optional[str] = "BR"


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    country: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserOut


# ─── Accounts ────────────────────────────────────────────────────────────────

class AccountOut(BaseModel):
    id: int
    currency: str
    balance: Decimal
    account_number: str
    is_active: bool
    created_at: datetime

    class Config:
        orm_mode = True


# ─── Transactions ────────────────────────────────────────────────────────────

class TransferRequest(BaseModel):
    receiver_email: str
    amount: Decimal
    currency_from: str
    currency_to: str
    description: Optional[str] = "Transferência WiseClone"


class TransactionOut(BaseModel):
    id: int
    amount: Decimal
    currency_from: str
    currency_to: str
    exchange_rate: Decimal
    amount_received: Decimal
    fee: Decimal
    description: Optional[str]
    status: str
    transaction_type: str
    created_at: datetime
    sender_id: Optional[int]
    receiver_id: Optional[int]

    class Config:
        orm_mode = True


# ─── Exchange ─────────────────────────────────────────────────────────────────

class ConvertRequest(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal


class ConvertResponse(BaseModel):
    from_currency: str
    to_currency: str
    amount: Decimal
    converted_amount: Decimal
    rate: Decimal
    fee: Decimal


class RateOut(BaseModel):
    currency_from: str
    currency_to: str
    rate: Decimal
    updated_at: datetime

    class Config:
        orm_mode = True
