from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative  import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import MetaData
from config import Config

DATABASE_URL = Config.HOST

engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

metadata = MetaData()


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session