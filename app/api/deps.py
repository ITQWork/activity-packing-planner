from typing import Generator
from app.db.session import Session, engine

def get_db() -> Generator:
    with Session(engine) as session:
        yield session
