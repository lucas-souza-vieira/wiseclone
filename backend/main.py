from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import traceback
import logging

from config import CORS_ORIGINS, DEBUG
from database import create_tables
from routes.auth_routes import router as auth_router
from routes.accounts import router as accounts_router
from routes.transactions import router as transactions_router
from routes.exchange import router as exchange_router

logging.basicConfig(level=logging.DEBUG if DEBUG else logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="WiseClone API",
    description="Banco internacional simulado — projeto DevSecOps acadêmico",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ⚠️  VULNERABILIDADE: CORS sem restrição de origem (allow_origins=["*"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    ⚠️  VULNERABILIDADE: Expõe stack trace completo nas respostas de erro.
    Em produção, nunca retorne detalhes internos ao cliente.
    """
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": str(exc),
            "traceback": traceback.format_exc(),  # Expõe estrutura interna
            "detail": "Erro interno do servidor",
        },
    )


@app.on_event("startup")
async def startup():
    logger.info("Iniciando WiseClone API...")
    create_tables()
    await seed_exchange_rates()
    logger.info("WiseClone API iniciada com sucesso.")


async def seed_exchange_rates():
    """Popula taxas de câmbio no banco de dados."""
    from database import SessionLocal
    from models import ExchangeRate
    from config import SUPPORTED_CURRENCIES

    rates_map = {
        ("BRL", "USD"): 0.180, ("BRL", "EUR"): 0.170, ("BRL", "GBP"): 0.140,
        ("BRL", "JPY"): 27.5, ("BRL", "ARS"): 185.0, ("BRL", "CAD"): 0.250,
        ("BRL", "CHF"): 0.160, ("USD", "BRL"): 5.55, ("USD", "EUR"): 0.940,
        ("USD", "GBP"): 0.780, ("USD", "JPY"): 152.0, ("EUR", "BRL"): 6.10,
        ("EUR", "USD"): 1.065, ("GBP", "BRL"): 7.20, ("GBP", "USD"): 1.28,
        ("JPY", "BRL"): 0.037, ("JPY", "USD"): 0.0066, ("ARS", "BRL"): 0.0054,
        ("CAD", "USD"): 0.73, ("CHF", "USD"): 1.12,
    }

    db = SessionLocal()
    try:
        existing = db.query(ExchangeRate).count()
        if existing == 0:
            for (c_from, c_to), rate in rates_map.items():
                db.add(ExchangeRate(currency_from=c_from, currency_to=c_to, rate=rate))
            db.commit()
            logger.info(f"Inseridas {len(rates_map)} taxas de câmbio.")
    finally:
        db.close()


app.include_router(auth_router)
app.include_router(accounts_router)
app.include_router(transactions_router)
app.include_router(exchange_router)


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "WiseClone API", "version": "1.0.0"}


@app.get("/")
def root():
    return {"message": "Bem-vindo à WiseClone API", "docs": "/docs"}
