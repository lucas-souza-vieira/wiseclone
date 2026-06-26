from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from typing import List
from database import get_db
from auth import get_current_user
from config import BASE_EXCHANGE_RATES
import models
import schemas

router = APIRouter(prefix="/exchange", tags=["Câmbio"])


def get_rate(db: Session, from_cur: str, to_cur: str) -> Decimal:
    """Busca taxa de câmbio do banco, fallback para taxas base."""
    if from_cur == to_cur:
        return Decimal("1.0")
    rate_row = db.query(models.ExchangeRate).filter(
        models.ExchangeRate.currency_from == from_cur,
        models.ExchangeRate.currency_to == to_cur,
    ).first()
    if rate_row:
        return Decimal(str(rate_row.rate))
    # Fallback usando taxas base (BRL como moeda pivot)
    brl_from = BASE_EXCHANGE_RATES.get(from_cur, 1.0)
    brl_to = BASE_EXCHANGE_RATES.get(to_cur, 1.0)
    if brl_from == 0:
        return Decimal("0")
    return Decimal(str(round(brl_to / brl_from, 6)))


@router.get("/rates", response_model=List[schemas.RateOut])
def list_rates(db: Session = Depends(get_db)):
    """Lista todas as taxas de câmbio disponíveis (endpoint público)."""
    rates = db.query(models.ExchangeRate).all()
    return rates


@router.get("/rates/{from_currency}/{to_currency}")
def get_specific_rate(
    from_currency: str,
    to_currency: str,
    db: Session = Depends(get_db),
):
    """Retorna a taxa de câmbio entre duas moedas."""
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    rate = get_rate(db, from_currency, to_currency)
    return {
        "from": from_currency,
        "to": to_currency,
        "rate": str(rate),
    }


@router.post("/convert", response_model=schemas.ConvertResponse)
def convert_currency(
    payload: schemas.ConvertRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Simula conversão de moeda (sem debitar saldo)."""
    from utils import calculate_fee
    from_c = payload.from_currency.upper()
    to_c = payload.to_currency.upper()

    rate = get_rate(db, from_c, to_c)
    fee = Decimal(str(calculate_fee(float(payload.amount), from_c, to_c)))
    net_amount = payload.amount - fee
    converted = (net_amount * rate).quantize(Decimal("0.01"))

    return {
        "from_currency": from_c,
        "to_currency": to_c,
        "amount": payload.amount,
        "converted_amount": converted,
        "rate": rate,
        "fee": fee,
    }
