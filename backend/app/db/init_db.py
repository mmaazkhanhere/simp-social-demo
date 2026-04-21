from sqlalchemy.orm import Session

from app.models import Base
from app.seed.dealerships import seed_dealerships


def init_db(engine, db: Session) -> None:
    Base.metadata.create_all(bind=engine)
    seed_dealerships(db)
    db.commit()

