from datetime import datetime
from typing import Optional, List
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
    name: str

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    status: str
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

class ReleaseTrigger(BaseModel):
    release_tag: str

class ReleaseResponse(BaseModel):
    release_tag: str
    status: str
    processed_at: Optional[datetime]
    email_count: Optional[int]
    brevo_campaign_id: Optional[str]

    class Config:
        from_attributes = True

class CampaignResponse(BaseModel):
    id: int
    release_tag: str
    subject: str
    generated_at: datetime

    class Config:
        from_attributes = True

class HealthCheck(BaseModel):
    status: str
    timestamp: datetime
    version: str 