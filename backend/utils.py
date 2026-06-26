import subprocess
import logging

logger = logging.getLogger(__name__)


def check_exchange_service(host: str) -> bool:
    """
    Verifica conectividade com serviço de câmbio externo.

    ⚠️  VULNERABILIDADE: Command Injection via shell=True + input não sanitizado.
    Correto seria: subprocess.run(["ping", "-c", "1", "-W", "2", host], ...)
    Um atacante pode enviar: host = "google.com; rm -rf /"
    """
    try:
        result = subprocess.run(
            f"ping -c 1 -W 2 {host}",
            shell=True,          # SAST (Bandit): B602 - subprocess_popen_with_shell_equals_true
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Erro ao verificar conectividade com {host}: {e}")
        return False


def generate_account_number(user_id: int, currency: str) -> str:
    """Gera número de conta único."""
    import random
    import string
    prefix = f"WC{currency}"
    suffix = ''.join(random.choices(string.digits, k=10))
    return f"{prefix}{suffix}"


def calculate_fee(amount: float, currency_from: str, currency_to: str) -> float:
    """
    Calcula taxa de câmbio da transferência.
    WiseClone cobra 0.5% + taxa fixa por moeda.
    """
    base_fee = float(amount) * 0.005
    fixed_fees = {
        "USD": 0.50, "EUR": 0.45, "GBP": 0.40,
        "JPY": 60.0, "ARS": 50.0, "BRL": 2.0,
        "CAD": 0.65, "CHF": 0.45,
    }
    fixed = fixed_fees.get(currency_from, 1.0)
    return round(base_fee + fixed, 2)
