from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = "sqlite:///./minos.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    from src.models.base import Base
    import src.models.source  # noqa: F401
    import src.models.portfolio  # noqa: F401
    import src.models.asset  # noqa: F401
    import src.models.position  # noqa: F401
    import src.models.load_record  # noqa: F401
    import src.models.portfolio_snapshot  # noqa: F401
    Base.metadata.create_all(engine)
    _ensure_sqlite_position_columns()


def _ensure_sqlite_position_columns():
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "positions" not in inspector.get_table_names():
        return

    existing = {column["name"] for column in inspector.get_columns("positions")}
    columns = {
        "unit_price": "FLOAT",
        "avg_cost": "FLOAT",
        "cost_basis": "FLOAT",
        "pnl_absolute": "FLOAT",
        "pnl_percentage": "FLOAT",
        "dpt": "FLOAT",
    }
    with engine.begin() as conn:
        for name, ddl_type in columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE positions ADD COLUMN {name} {ddl_type}"))
