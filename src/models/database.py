from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.config.settings import settings

# Create async engine with aiomysql
# Get the actual database URL string value
db_url_str = str(settings.DATABASE_URL)

# Convert mysql:// to mysql+aiomysql:// in the connection URL
if db_url_str.startswith('mysql://'):
    db_url = db_url_str.replace('mysql://', 'mysql+aiomysql://', 1)
elif 'aiomysql' not in db_url_str:
    db_url = f'mysql+aiomysql{db_url_str[5:]}' if db_url_str.startswith('mysql+') else f'mysql+aiomysql://{db_url_str}'
else:
    db_url = db_url_str

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    pool_recycle=3600,
    pool_pre_ping=True
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

class ReleasesProcessed(Base):
    """Processed releases table"""
    __tablename__ = "releases_processed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), unique=True, nullable=False)
    processed_at = Column(DateTime, default=datetime.now(timezone.utc))
    status = Column(Enum("processing", "completed", "failed", name="release_status"), default="processing")
    brevo_campaign_id = Column(String(100))
    email_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

    email_content = relationship("EmailContent", back_populates="release")

class Users(Base):
    """Users table"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    status = Column(Enum("active", "inactive", name="user_status"), default="active")
    created_at = Column(DateTime, default=datetime.now(timezone.utc))

class EmailContent(Base):
    """Email content table"""
    __tablename__ = "email_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), ForeignKey("releases_processed.release_tag"), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.now(timezone.utc))

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