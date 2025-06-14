from datetime import datetime
from typing import List, Optional, AsyncGenerator
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.database import ReleasesProcessed, Users, EmailContent
from src.models.schemas import (
    UserCreate, UserResponse, ReleaseResponse, CampaignResponse,
    ReleaseTrigger, HealthCheck
)
from src.agents.graph import get_workflow
from src.config.settings import settings
from src.utils.logger import setup_logger
from src.models.database import get_db_session

logger = setup_logger(__name__)
app = FastAPI(title="ReleaseBot AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function that yields db sessions.
    This is a wrapper around get_db_session for FastAPI's dependency injection.
    """
    async for session in get_db_session():
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        

@app.post("/trigger-release", response_model=ReleaseResponse)
async def trigger_release(
    trigger: ReleaseTrigger,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    try:
        workflow = get_workflow()
        state = {
            'release_tag': trigger.release_tag,
            'manual_trigger': True,
            'errors': [],
            'retry_count': 0
        }
        
        background_tasks.add_task(workflow.run, state)
        
        return {
            'release_tag': trigger.release_tag,
            'status': 'processing',
            'triggered_at': datetime.utcnow()
        }
    except Exception as e:
        logger.error(f"Error triggering release: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/releases", response_model=List[ReleaseResponse])
async def get_releases(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        releases = await db.query(ReleasesProcessed).order_by(
            ReleasesProcessed.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [
            {
                'release_tag': r.release_tag,
                'status': r.status,
                'processed_at': r.processed_at,
                'email_count': r.email_count,
                'brevo_campaign_id': r.brevo_campaign_id
            }
            for r in releases
        ]
    except Exception as e:
        logger.error(f"Error fetching releases: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/releases/{tag}/status", response_model=ReleaseResponse)
async def get_release_status(
    tag: str,
    db: AsyncSession = Depends(get_db)
):
    try:
        release = await db.query(ReleasesProcessed).filter(
            ReleasesProcessed.release_tag == tag
        ).first()
        
        if not release:
            raise HTTPException(status_code=404, detail="Release not found")
            
        return {
            'release_tag': release.release_tag,
            'status': release.status,
            'processed_at': release.processed_at,
            'email_count': release.email_count,
            'brevo_campaign_id': release.brevo_campaign_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching release status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/users", response_model=List[UserResponse])
async def get_users(
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        query = db.query(Users)
        if status:
            query = query.filter(Users.status == status)
            
        users = await query.offset(offset).limit(limit).all()
        
        return [
            {
                'email': u.email,
                'name': u.name,
                'status': u.status,
                'created_at': u.created_at
            }
            for u in users
        ]
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/users", response_model=UserResponse)
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_user = Users(
            email=user.email,
            name=user.name,
            status='active'
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        
        return {
            'email': db_user.email,
            'name': db_user.name,
            'status': db_user.status,
            'created_at': db_user.created_at
        }
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    try:
        campaigns = await db.query(EmailContent).order_by(
            EmailContent.generated_at.desc()
        ).offset(offset).limit(limit).all()
        
        return [
            {
                'id': c.id,
                'release_tag': c.release_tag,
                'subject': c.subject,
                'generated_at': c.generated_at
            }
            for c in campaigns
        ]
    except Exception as e:
        logger.error(f"Error fetching campaigns: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health", response_model=HealthCheck)
async def health_check():
    try:
        return {
            'status': 'healthy',
            'timestamp': datetime.utcnow(),
            'version': settings.APP_VERSION
        }
    except Exception as e:
        logger.error(f"Error in health check: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e)) 