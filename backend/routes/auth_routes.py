from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from auth import hash_password, verify_password, create_access_token, get_current_user
from utils import generate_account_number
from config import SUPPORTED_CURRENCIES
import models
import schemas

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post("/register", response_model=schemas.Token, status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserCreate, db: Session = Depends(get_db)):
    """Cadastra novo usuário e cria carteiras para todas as moedas suportadas."""
    existing = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")

    user = models.User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        phone=user_data.phone,
        country=user_data.country or "BR",
    )
    db.add(user)
    db.flush()

    # Criar contas para cada moeda suportada
    for currency in SUPPORTED_CURRENCIES:
        initial_balance = 1000.00 if currency == "BRL" else (
            500.00 if currency == "USD" else
            450.00 if currency == "EUR" else
            0.00
        )
        account = models.Account(
            user_id=user.id,
            currency=currency,
            balance=initial_balance,
            account_number=generate_account_number(user.id, currency),
        )
        db.add(account)

    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.post("/login", response_model=schemas.Token)
def login(credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    """Autentica usuário e retorna token JWT."""
    user = db.query(models.User).filter(models.User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Conta desativada")

    token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer", "user": user}


@router.get("/me", response_model=schemas.UserOut)
def me(current_user: models.User = Depends(get_current_user)):
    """Retorna dados do usuário autenticado."""
    return current_user
