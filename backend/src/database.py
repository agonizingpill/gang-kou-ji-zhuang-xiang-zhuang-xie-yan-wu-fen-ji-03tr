import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from redis import Redis

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://port_ops:port_ops_local@db:5432/port_ops")
REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)

class Base(DeclarativeBase):
    pass

# create_all 只建新表，已为存量库补齐 delay_cases 的门槛/核级列
_COLUMN_UPGRADES = [
    "ALTER TABLE delay_cases ADD COLUMN IF NOT EXISTS threshold_version INTEGER",
    "ALTER TABLE delay_cases ADD COLUMN IF NOT EXISTS threshold_value DOUBLE PRECISION",
    "ALTER TABLE delay_cases ADD COLUMN IF NOT EXISTS threshold_bound_at TIMESTAMPTZ",
    "ALTER TABLE delay_cases ADD COLUMN IF NOT EXISTS reviewed_by VARCHAR(40)",
    "ALTER TABLE delay_cases ADD COLUMN IF NOT EXISTS reviewed_at TIMESTAMPTZ",
]

def ensure_schema_upgrades():
    if engine.dialect.name != "postgresql":
        return
    with engine.begin() as conn:
        for statement in _COLUMN_UPGRADES:
            conn.execute(text(statement))
