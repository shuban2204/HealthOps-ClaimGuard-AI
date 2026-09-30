from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.config import DATABASE_URL


class Base(DeclarativeBase):
    pass


class ClaimRecord(Base):
    __tablename__ = "claims"

    claim_id: Mapped[str] = mapped_column(String, primary_key=True)
    claim_type: Mapped[str] = mapped_column(String, index=True)
    provider_network: Mapped[str] = mapped_column(String, index=True)
    risk_band: Mapped[str] = mapped_column(String, index=True)
    is_anomaly: Mapped[bool] = mapped_column(Boolean, index=True)

    claim_payment_amount: Mapped[float] = mapped_column(Float)
    claim_total_charge: Mapped[float] = mapped_column(Float)
    claim_duration_days: Mapped[int] = mapped_column(Integer)
    diagnosis_count: Mapped[int] = mapped_column(Integer)
    procedure_count: Mapped[int] = mapped_column(Integer)
    reimbursement_ratio: Mapped[float] = mapped_column(Float)

    prior_auth_required: Mapped[bool] = mapped_column(Boolean)
    prior_auth_present: Mapped[bool] = mapped_column(Boolean)
    documentation_complete: Mapped[bool] = mapped_column(Boolean)
    coding_mismatch_flag: Mapped[bool] = mapped_column(Boolean)
    duplicate_claim_flag: Mapped[bool] = mapped_column(Boolean)
    member_coverage_active: Mapped[bool] = mapped_column(Boolean)
    timely_filing_flag: Mapped[bool] = mapped_column(Boolean)
    historical_provider_denial_rate: Mapped[float] = mapped_column(Float)

    denial_probability: Mapped[float] = mapped_column(Float, index=True)
    anomaly_score: Mapped[float] = mapped_column(Float)
    denied: Mapped[int] = mapped_column(Integer)
    claim_json: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope():
    session: Session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

