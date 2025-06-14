from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class ReleasesProcessed(Base):
    __tablename__ = "releases_processed"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), unique=True, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)
    status = Column(Enum("processing", "completed", "failed", name="release_status"), default="processing")
    brevo_campaign_id = Column(String(100))
    email_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    email_content = relationship("EmailContent", back_populates="release")

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    status = Column(Enum("active", "inactive", name="user_status"), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class EmailContent(Base):
    __tablename__ = "email_content"

    id = Column(Integer, primary_key=True, autoincrement=True)
    release_tag = Column(String(50), ForeignKey("releases_processed.release_tag"), nullable=False)
    subject = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    release = relationship("ReleasesProcessed", back_populates="email_content") 