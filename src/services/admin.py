from sqlalchemy.orm import Session

from src.models.load_record import LoadRecord
from src.models.position import Position

LOCAL_LOAD_TYPES = ("file", "manual")


def reset_uploaded_data(db: Session) -> dict[str, int | list[str]]:
    positions_deleted = (
        db.query(Position)
        .filter(Position.load_type.in_(LOCAL_LOAD_TYPES))
        .delete(synchronize_session=False)
    )
    load_records_deleted = (
        db.query(LoadRecord)
        .filter(LoadRecord.load_type.in_(LOCAL_LOAD_TYPES))
        .delete(synchronize_session=False)
    )
    db.commit()

    return {
        "positions_deleted": positions_deleted,
        "load_records_deleted": load_records_deleted,
        "preserved_load_types": ["api", "visual"],
    }
