from sqlalchemy import create_engine
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
    Base.metadata.create_all(engine)
