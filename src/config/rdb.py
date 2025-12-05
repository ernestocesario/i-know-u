import os
from sqlmodel import SQLModel, create_engine, Session

DATA_DIR = "data"
DB_NAME = "iku_database.db"
DB_URL = f"sqlite:///{DATA_DIR}/{DB_NAME}"

engine = create_engine(DB_URL, echo=True, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    SQLModel.metadata.create_all(engine)