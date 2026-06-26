from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from auth import get_current_user
from typing import List
import models
import schemas

router = APIRouter(prefix="/accounts", tags=["Contas"])


@router.get("/", response_model=List[schemas.AccountOut])
def list_accounts(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todas as contas/carteiras do usuário."""
    accounts = db.query(models.Account).filter(
        models.Account.user_id == current_user.id,
        models.Account.is_active == True,
    ).all()
    return accounts


@router.get("/{account_id}", response_model=schemas.AccountOut)
def get_account(
    account_id: int,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retorna detalhes de uma conta específica.
    ⚠️  VULNERABILIDADE (IDOR): Não verifica se a conta pertence ao usuário autenticado.
    Qualquer usuário logado pode acessar contas de outros usuários.
    """
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada")
    # Falta verificar: if account.user_id != current_user.id: raise 403
    return account


@router.get("/summary/all")
def accounts_summary(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retorna resumo de saldos de todas as carteiras do usuário."""
    accounts = db.query(models.Account).filter(
        models.Account.user_id == current_user.id,
        models.Account.is_active == True,
    ).all()

    total_brl = sum(
        float(a.balance) for a in accounts if a.currency == "BRL"
    )

    return {
        "user": current_user.full_name,
        "accounts": [
            {
                "currency": a.currency,
                "balance": float(a.balance),
                "account_number": a.account_number,
            }
            for a in accounts
        ],
        "total_brl_equivalent": total_brl,
    }
