import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Run(Base):
    __tablename__ = "runs"
    __table_args__ = (
        UniqueConstraint(
            "strategy",
            "seed",
            "gamma",
            "sigma",
            "k",
            "A",
            "inventory_limit",
            "min_quote_spread",
            "max_quote_distance",
            "volatility_spread_multiplier",
            "inventory_skew",
            "adverse_selection_strength",
            name="uq_runs_strategy_seed_params",
        ),
    )

    run_id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    strategy: Mapped[str] = mapped_column(String, nullable=False)
    seed: Mapped[int] = mapped_column(Integer, nullable=False)
    gamma: Mapped[float | None] = mapped_column(Float, nullable=True)
    sigma: Mapped[float | None] = mapped_column(Float, nullable=True)
    k: Mapped[float | None] = mapped_column(Float, nullable=True)
    A: Mapped[float | None] = mapped_column(Float, nullable=True)
    inventory_limit: Mapped[int | None] = mapped_column(Integer, nullable=True)
    min_quote_spread: Mapped[float | None] = mapped_column(Float, nullable=True)
    max_quote_distance: Mapped[float | None] = mapped_column(Float, nullable=True)
    volatility_spread_multiplier: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    inventory_skew: Mapped[float | None] = mapped_column(Float, nullable=True)
    adverse_selection_strength: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )
    net_pnl: Mapped[float] = mapped_column(Float, nullable=False)
    sharpe: Mapped[float] = mapped_column(Float, nullable=False)
    sortino: Mapped[float] = mapped_column(Float, nullable=False)
    max_drawdown: Mapped[float] = mapped_column(Float, nullable=False)
    max_abs_inventory: Mapped[float] = mapped_column(Float, nullable=False)
    fees_paid: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
    )
