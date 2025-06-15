from datetime import datetime, timezone
from typing import AsyncGenerator
import os

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.config.settings import settings

# Create async engine with asyncpg
db_url = str(settings.DATABASE_URL)

# Ensure the URL uses asyncpg for PostgreSQL
if db_url.startswith('postgresql://'):
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://', 1)
elif not db_url.startswith('postgresql+asyncpg://'):
    db_url = f'postgresql+asyncpg://{db_url}'

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# Define enums for PostgreSQL
release_status_enum = PgEnum(
    'release_status',
    name='release_status',
    create_type=True
)

user_status_enum = PgEnum(
    'user_status',
    name='user_status',
    create_type=True
)

class ReleasesProcessed(Base):
    """Processed releases table"""
    __tablename__ = "releases_processed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), unique=True, nullable=False)
    processed_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))
    status = Column(release_status_enum, default="processing")
    brevo_campaign_id = Column(String(100))
    email_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    email_content = relationship("EmailContent", back_populates="release")

class Users(Base):
    """Users table"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    status = Column(user_status_enum, default="active")
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

class EmailContent(Base):
    """Email content table"""
    __tablename__ = "email_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), ForeignKey("releases_processed.release_tag", ondelete="CASCADE"), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))

    release = relationship("ReleasesProcessed", back_populates="email_content")


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator that yields database sessions.
    
    Yields:
        AsyncSession: A database session instance
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()