from typing import Dict, Any, List, ClassVar, Optional
from langchain.tools import BaseTool
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import Field

from src.utils.logger import setup_logger, log_execution_time
from src.services.brevo_service import BrevoService
from src.models.database import get_db_session
from src.models.database import Users, ReleasesProcessed, EmailContent
from src.utils.helpers import retry_with_backoff

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
        users = await self.brevo_service.get_contacts()
        return [user for user in users if user["status"] == "active"]

    @retry_with_backoff()
    async def _create_campaign(
        self,
        subject: str,
        content: str,
        recipients: List[Dict[str, Any]]
    ) -> str:
        campaign = await self.brevo_service.create_campaign(
            subject=subject,
            content=content,
            recipients=recipients
        )
        return campaign["id"]

    @retry_with_backoff()
    async def _update_campaign_status(self, campaign_id: str) -> None:
        await self.brevo_service.update_campaign_status(campaign_id)

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 