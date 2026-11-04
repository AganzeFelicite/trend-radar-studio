from decimal import Decimal

from sqlalchemy import text

from studio.config import COST_CAPS_USD
from studio.db import engine


class BudgetExceeded(RuntimeError):
    """Raised before a paid call that would push a service past its monthly cap."""


def month_to_date(service: str) -> Decimal:
    with engine.connect() as c:
        return c.scalar(
            text("select coalesce(sum(usd), 0) from costs where service = :s and created_at >= date_trunc('month', now())"),
            {"s": service},
        )


# ponytail: check-then-spend is not atomic; fine with one worker, add a row lock if workers > 1.
def ensure_budget(service: str, estimate_usd: Decimal | str) -> None:
    spent, cap, estimate = month_to_date(service), COST_CAPS_USD[service], Decimal(estimate_usd)
    if spent + estimate > cap:
        raise BudgetExceeded(f"{service} monthly cap ${cap} reached: ${spent} spent, this call needs ~${estimate}")


def record_cost(service: str, provider: str, usd: Decimal | str, *, job_id: int | None = None,
                quantity: Decimal | None = None, unit: str | None = None, note: str | None = None) -> None:
    with engine.begin() as c:
        c.execute(
            text("insert into costs (job_id, service, provider, usd, quantity, unit, note)"
                 " values (:job_id, :service, :provider, :usd, :quantity, :unit, :note)"),
            {"job_id": job_id, "service": service, "provider": provider, "usd": Decimal(usd),
             "quantity": quantity, "unit": unit, "note": note},
        )
