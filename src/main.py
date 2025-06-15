from datetime import datetime
from typing import List, Optional, AsyncGenerator
from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.models.database import ReleasesProcessed, Users, EmailContent
from src.models.schemas import (
    UserCreate, UserResponse, ReleaseResponse, CampaignResponse,
    ReleaseTrigger
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
        result = await db.execute(
            select(ReleasesProcessed)
            .order_by(ReleasesProcessed.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        releases = result.scalars().all()
        
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
        result = await db.execute(
            select(ReleasesProcessed)
            .where(ReleasesProcessed.release_tag == tag)
        )
        release = result.scalar_one_or_none()
        
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
        stmt = select(Users)
        if status:
            stmt = stmt.where(Users.status == status)
            
        result = await db.execute(
            stmt.offset(offset).limit(limit)
        )
        users = result.scalars().all()
        
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
        result = await db.execute(
            select(EmailContent)
            .order_by(EmailContent.generated_at.desc())
            .offset(offset)
            .limit(limit)
        )
        campaigns = result.scalars().all()
        
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

async def check_database_health(db: AsyncSession) -> bool:
    """Check if database is accessible by making a simple query."""
    try:
        await db.execute(select(1))
        return True
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return False

@app.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    try:
        db_status = await check_database_health(db)
        status = 'healthy' if db_status else 'unhealthy'
        status_code = 200 if db_status else 503
        
        # Convert datetime to ISO format string for JSON serialization
        response = {
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'version': settings.APP_VERSION,
            'database': 'connected' if db_status else 'disconnected'
        }
        
        if not db_status:
            response['error'] = 'Database connection failed'
            
        from fastapi.responses import JSONResponse
        return JSONResponse(
            content=response,
            status_code=status_code
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                'status': 'error',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
        )