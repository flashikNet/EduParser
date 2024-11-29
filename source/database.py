from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from models import Base

DATABASE_URL = "sqlite+aiosqlite:///./sneakers.db"

# Асинхронный движок и сессия
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Создание таблиц в БД
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
