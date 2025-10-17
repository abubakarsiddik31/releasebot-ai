from datetime import datetime, timezone
from typing import AsyncGenerator

from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from src.config.settings import settings

# Create async engine with appropriate driver
db_url = str(settings.DATABASE_URL)

# Determine database type and adjust URL accordingly
if db_url.startswith("postgresql://"):
    # Convert to async PostgreSQL URL
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    db_type = "postgresql"
elif db_url.startswith("mysql://"):
    # Convert to async MySQL URL
    db_url = db_url.replace("mysql://", "mysql+aiomysql://", 1)
    db_type = "mysql"
elif db_url.startswith("postgresql+asyncpg://"):
    # Already in correct format
    db_type = "postgresql"
elif db_url.startswith("mysql+aiomysql://"):
    # Already in correct format
    db_type = "mysql"
else:
    # Default to PostgreSQL if not specified
    db_url = f"postgresql+asyncpg://{db_url}"
    db_type = "postgresql"

engine = create_async_engine(
    db_url,
    echo=settings.DEBUG,
    pool_recycle=3600,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=10,
)

# Create async session factory
async_session_factory = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

Base = declarative_base()

# Define enums based on database type
if db_type == "postgresql":
    release_status_enum = PgEnum(
        "release_status",
        name="release_status",
        values=("processing", "completed", "failed"),
        create_type=True,
    )

    user_status_enum = PgEnum(
        "user_status",
        name="user_status",
        values=("active", "inactive", "bounced", "unsubscribed"),
        create_type=True,
    )
else:  # MySQL
    release_status_enum = Enum(
        "processing", "completed", "failed", name="release_status"
    )

    user_status_enum = Enum(
        "active", "inactive", "bounced", "unsubscribed", name="user_status"
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
    created_at = Column(DateTime(timezone=True), default=datetime.now(timezone.utc))


class EmailContent(Base):
    """Email content table"""

    __tablename__ = "email_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(
        String(50),
        ForeignKey("releases_processed.release_tag", ondelete="CASCADE"),
        nullable=False,
    )
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
