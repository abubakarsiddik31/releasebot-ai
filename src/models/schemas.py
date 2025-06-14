from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr

class ReleaseBase(BaseModel):
    release_tag: str
    status: str
    brevo_campaign_id: Optional[str] = None
    email_count: int = 0

class ReleaseCreate(ReleaseBase):
    pass

class Release(ReleaseBase):
    id: int
    processed_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    status: str = "active"

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class EmailContentBase(BaseModel):
    release_tag: str
    subject: str
    content: str

class EmailContentCreate(EmailContentBase):
    pass

class EmailContent(EmailContentBase):
    id: int
    generated_at: datetime

    class Config:
        from_attributes = True 