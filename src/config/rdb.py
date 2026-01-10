import os
from sqlmodel import SQLModel, create_engine, Session

from src.config.app_properties import AppProperties

DATA_DIR = AppProperties.DATA_DIR

DB_NAME = "iku_database.db"
DB_URL = f"sqlite:///{DATA_DIR}/{DB_NAME}"

engine = create_engine(DB_URL, echo=False, connect_args={"check_same_thread": False})


def get_session():
    with Session(engine) as session:
        yield session


def create_db_and_tables():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    SQLModel.metadata.create_all(engine)