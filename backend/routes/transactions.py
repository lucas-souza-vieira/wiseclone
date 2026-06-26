from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from decimal import Decimal
from database import get_db
from auth import get_current_user
from utils import calculate_fee
from typing import List
import models
import schemas

router = APIRouter(prefix="/transactions", tags=["Transações"])


@router.post("/transfer", response_model=schemas.TransactionOut)
def transfer(
    payload: schemas.TransferRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Realiza transferência entre usuários com câmbio automático."""
    if payload.currency_from not in ["BRL", "USD", "EUR", "GBP", "JPY", "ARS", "CAD", "CHF"]:
        raise HTTPException(status_code=400, detail="Moeda de origem inválida")

    receiver = db.query(models.User).filter(models.User.email == payload.receiver_email).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Destinatário não encontrado")
    if receiver.id == current_user.id:
        raise HTTPException(status_code=400, detail="Não é possível transferir para si mesmo")

    sender_account = db.query(models.Account).filter(
        models.Account.user_id == current_user.id,
        models.Account.currency == payload.currency_from,
        models.Account.is_active == True,
    ).first()
    if not sender_account:
        raise HTTPException(status_code=404, detail="Carteira de origem não encontrada")

    fee = Decimal(str(calculate_fee(float(payload.amount), payload.currency_from, payload.currency_to)))
    total_debit = payload.amount + fee
    if sender_account.balance < total_debit:
        raise HTTPException(status_code=400, detail="Saldo insuficiente")

    rate_row = db.query(models.ExchangeRate).filter(
        models.ExchangeRate.currency_from == payload.currency_from,
        models.ExchangeRate.currency_to == payload.currency_to,
    ).first()
    rate = Decimal(str(rate_row.rate)) if rate_row else Decimal("1.0")
    amount_received = (payload.amount * rate).quantize(Decimal("0.01"))

    receiver_account = db.query(models.Account).filter(
        models.Account.user_id == receiver.id,
        models.Account.currency == payload.currency_to,
        models.Account.is_active == True,
    ).first()
    if not receiver_account:
        raise HTTPException(status_code=404, detail="Destinatário não possui carteira na moeda destino")

    sender_account.balance -= total_debit
    receiver_account.balance += amount_received

    tx = models.Transaction(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        sender_account_id=sender_account.id,
        receiver_account_id=receiver_account.id,
        amount=payload.amount,
        currency_from=payload.currency_from,
        currency_to=payload.currency_to,
        exchange_rate=rate,
        amount_received=amount_received,
        fee=fee,
        description=payload.description,
        status="completed",
        transaction_type="transfer",
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


@router.get("/", response_model=List[schemas.TransactionOut])
def list_transactions(
    limit: int = 20,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista as transações do usuário autenticado."""
    txs = db.query(models.Transaction).filter(
        (models.Transaction.sender_id == current_user.id) |
        (models.Transaction.receiver_id == current_user.id)
    ).order_by(models.Transaction.created_at.desc()).limit(limit).all()
    return txs


@router.get("/search")
def search_transactions(
    q: str = Query(..., description="Termo de busca na descrição"),
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Busca transações por descrição.

    ⚠️  VULNERABILIDADE: SQL Injection por concatenação de string.
    A variável `q` é inserida diretamente na query sem sanitização.
    Exemplo de ataque: q = "' OR '1'='1"

    Correto seria:
        db.execute(text("SELECT ... WHERE description LIKE :q"), {"q": f"%{q}%"})
    """
    raw_query = (
        f"SELECT id, amount, currency_from, currency_to, description, status, created_at "
        f"FROM transactions "
        f"WHERE (sender_id = {current_user.id} OR receiver_id = {current_user.id}) "
        f"AND description LIKE '%{q}%' "
        f"ORDER BY created_at DESC LIMIT 50"
    )
    result = db.execute(text(raw_query))
    rows = result.fetchall()
    return [
        {
            "id": r[0], "amount": str(r[1]), "currency_from": r[2],
            "currency_to": r[3], "description": r[4], "status": r[5],
            "created_at": str(r[6]),
        }
        for r in rows
    ]
