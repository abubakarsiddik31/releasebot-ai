from typing import Dict, Any, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.utils.logger import setup_logger
from src.services.brevo_service import BrevoService
from src.models.database import get_db_session
from src.models.database import Users, ReleasesProcessed, EmailContent

logger = setup_logger(__name__)

class EmailDistributor:
    """Email distributor agent"""
    def __init__(self):
        self.brevo_service = BrevoService()
        self.max_retries = 3

    async def distribute_emails(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Distribute emails for a release
        
        Args:
            state: Current state containing release information
            
        Returns:
            Updated state with distribution results
        """
        try:
            logger.info(f"Starting email distribution for release {state.get('release_tag')}")
            
            if not state.get('approved', False):
                raise ValueError("Content not approved for distribution")

            # Get a database session
            session_gen = get_db_session()
            session = await anext(session_gen)
            
            try:
                users = await self._get_active_users(session)
                campaign = await self._create_campaign(state, session)
                
                if not users:
                    raise ValueError("No active users found for distribution")

                results = await self.brevo_service.send_bulk_emails(
                    recipients=[{'email': user.email, 'name': user.name} for user in users],
                    subject=state['email_subject'],
                    html_content=state['email_content'],
                    campaign_id=campaign.id
                )

                await self._update_campaign_status(session, campaign.id, results)
                state['send_status'] = 'completed'
                state['email_count'] = len(results['success'])
                state['brevo_campaign_id'] = campaign.id

                if results['failed']:
                    logger.warning(f"Failed to send {len(results['failed'])} emails")
                    state['errors'].extend([f"Failed to send to {f['email']}: {f['error']}" for f in results['failed']])

                return state
                
            finally:
                await session.close()
                await session_gen.aclose()

        except Exception as e:
            logger.error(f"Error in email distribution: {str(e)}")
            state['errors'].append(f"Email distribution failed: {str(e)}")
            state['send_status'] = 'failed'
            return state

    async def _get_active_users(self, session: AsyncSession) -> List[Users]:
        """
        Get all active users from the database
        
        Args:
            session: Database session
            
        Returns:
            List of active users
        """
        try:
            query = select(Users).where(Users.status == 'active')
            result = await session.execute(query)
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error fetching active users: {str(e)}")
            raise

    async def _create_campaign(
        self,
        state: Dict[str, Any],
        session: AsyncSession
    ) -> EmailContent:
        """
        Create a new email campaign in the database
        
        Args:
            state: Current state with campaign details
            session: Database session
            
        Returns:
            Created EmailContent instance
        """
        try:
            campaign = EmailContent(
                release_tag=state['release_tag'],
                subject=state['email_subject'],
                content=state['email_content'],
                generated_at=state.get('generated_at')
            )
            session.add(campaign)
            await session.commit()
            await session.refresh(campaign)
            return campaign
        except Exception as e:
            logger.error(f"Error creating campaign: {str(e)}")
            raise

    async def _update_campaign_status(
        self,
        session: AsyncSession,
        campaign_id: str,
        results: Dict[str, Any]
    ) -> None:
        """
        Update the status of a campaign in the database
        
        Args:
            session: Database session
            campaign_id: ID of the campaign to update
            results: Dictionary containing success/failure results
        """
        try:
            release = await session.get(ReleasesProcessed, campaign_id)
            if release:
                release.status = 'completed'
                release.email_count = len(results['success'])
                await session.commit()
        except Exception as e:
            logger.error(f"Error updating campaign status: {str(e)}")
            raise

    async def _handle_bounce(self, email: str, session: AsyncSession) -> None:
        """
        Handle email bounce by updating user status
        
        Args:
            email: Email address that bounced
            session: Database session
        """
        try:
            user = await session.get(Users, email)
            if user:
                user.status = 'bounced'
                await session.commit()
        except Exception as e:
            logger.error(f"Error handling bounce for {email}: {str(e)}")
            raise

    async def _handle_unsubscribe(self, email: str, session: AsyncSession) -> None:
        """
        Handle user unsubscribe by updating user status
        
        Args:
            email: Email address to unsubscribe
            session: Database session
        """
        try:
            user = await session.get(Users, email)
            if user:
                user.status = 'unsubscribed'
                await session.commit()
        except Exception as e:
            logger.error(f"Error handling unsubscribe for {email}: {str(e)}")
            raise 