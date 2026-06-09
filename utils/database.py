import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from placement_ai.utils.config import settings
from placement_ai.utils.models import Base

# Try async engine, fall back to sync
try:
    from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
    async_engine = create_async_engine(settings.DATABASE_URL, echo=False)
    AsyncSessionLocal = async_sessionmaker(async_engine, expire_on_commit=False)
    ASYNC_AVAILABLE = True
except Exception:
    ASYNC_AVAILABLE = False

# Sync engine always available
sync_engine = create_engine(settings.SYNC_DATABASE_URL, echo=False)
SyncSession = sessionmaker(bind=sync_engine)

async def get_db():
    if ASYNC_AVAILABLE:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    else:
        with SyncSession() as session:
            yield session

async def init_db():
    if ASYNC_AVAILABLE:
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    else:
        Base.metadata.create_all(sync_engine)
