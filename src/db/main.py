from fastapi import FastAPI
from src.config import Config
from sqlmodel import create_engine, SQLModel, Session
from contextlib import asynccontextmanager

engine = create_engine(Config.DATABASE_URL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables in the database
    SQLModel.metadata.create_all(engine)
    yield
    # Any cleanup can be done here


def get_session():
    with Session(engine) as session:
        yield session
