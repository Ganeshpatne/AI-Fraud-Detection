"""
Async SQLAlchemy database engine & session factory.
Supports both PostgreSQL (production) and SQLite (local dev).
"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from backend.config import DATABASE_URL, USE_SQLITE

# SQLite needs connect_args for async
engine_kwargs = {"echo": False}
if USE_SQLITE:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    engine_kwargs["pool_size"] = 20
    engine_kwargs["max_overflow"] = 10

engine = create_async_engine(DATABASE_URL, **engine_kwargs)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""
    pass


async def get_db():
    """FastAPI dependency – yields an async DB session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Create all tables (used on startup) and seed default admin user."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    try:
        from backend.models.database_models import User
        from backend.utils.auth import hash_password
        from sqlalchemy import select
        async with async_session() as session:
            result = await session.execute(select(User).where(User.username == "admin"))
            if not result.scalar_one_or_none():
                admin_user = User(
                    username="admin",
                    email="admin@example.com",
                    password_hash=hash_password("admin123"),
                    role="admin",
                    is_active=True,
                )
                session.add(admin_user)
                await session.commit()
    except Exception:
        pass

