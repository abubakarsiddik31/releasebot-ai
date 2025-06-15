from typing import Dict, Any, List, ClassVar, Optional
from datetime import datetime
from langchain.tools import BaseTool
from sqlalchemy import select
from pydantic import Field

from src.utils.logger import setup_logger, log_execution_time
from src.services.brevo_service import BrevoService
from src.models.database import Users
from src.utils.helpers import retry_with_backoff
from src.services.database_service import get_db

logger = setup_logger(__name__, "email_distributor.log")

class EmailDistributor(BaseTool):
    name: ClassVar[str] = "email_distributor"
    description: ClassVar[str] = "Distributes emails to users"
    brevo_service: Optional[BrevoService] = Field(default=None)
    max_retries: int = 3
    
    def __init__(self):
        super().__init__()
        self.brevo_service = BrevoService()

    @log_execution_time(logger)
    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["email_content"] or not state["email_subject"]:
                return {"error": "Missing email content or subject"}

            active_users = await self._get_active_users()
            if not active_users:
                return {"error": "No active users found"}

            campaign_id = await self._create_campaign(
                state["email_subject"],
                state["email_content"],
                active_users
            )

            await self._update_campaign_status(campaign_id)
            return {
                "campaign_id": campaign_id,
                "send_status": "completed"
            }

        except Exception as e:
            logger.error(f"Error in email distribution: {str(e)}")
            return {
                "error": str(e),
                "send_status": "failed"
            }

    @retry_with_backoff()
    async def _get_active_users(self) -> List[Dict[str, Any]]:
        """
        Fetch active users from the database.
        
        Returns:
            List[Dict[str, Any]]: List of user dictionaries containing email and name
        """
        
        async with get_db() as session:
            try:
                # Query active users
                result = await session.execute(
                    select(Users)
                    .order_by(Users.email)
                )
                users = result.scalars().all()
                
                # Convert SQLAlchemy models to dictionaries
                return [
                    {
                        'email': user.email,
                        'name': user.name or user.email.split('@')[0],
                        'created_at': user.created_at.isoformat() if user.created_at else None
                    }
                for user in users
            ]
            
            except Exception as e:
                logger.error(f"Error fetching users from database: {str(e)}")
                raise

    @retry_with_backoff()
    async def _create_campaign(
        self,
        subject: str,
        content: str,
        recipients: List[Dict[str, Any]]
    ) -> str:
        # Generate a campaign name based on subject and timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        campaign_name = f"{subject[:50]}_{timestamp}"
        
        # Create the campaign using Brevo service
        campaign = await self.brevo_service.create_campaign(
            name=campaign_name,
            subject=subject,
            html_content=content
        )
        return campaign["campaign_id"]

    @retry_with_backoff()
    async def _update_campaign_status(self, campaign_id: str, status: str = "scheduled") -> Dict[str, Any]:
        """
        Update the status of a campaign in Brevo.
        
        Args:
            campaign_id: The ID of the campaign to update
            status: The new status ('scheduled' or 'sent')
            
        Returns:
            Dict containing the updated campaign status
        """
        if not self.brevo_service:
            raise ValueError("Brevo service is not initialized")
            
        return await self.brevo_service.update_campaign_status(campaign_id, status)

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 