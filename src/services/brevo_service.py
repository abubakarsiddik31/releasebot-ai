from typing import List, Dict, Any, Optional
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__)

class BrevoService:
    def __init__(self):
        self.configuration = sib_api_v3_sdk.Configuration()
        self.configuration.api_key['api-key'] = settings.BREVO_API_KEY
        self.api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        self.contacts_api = sib_api_v3_sdk.ContactsApi(sib_api_v3_sdk.ApiClient(self.configuration))
        self.batch_size = 50
        self.max_retries = 3

    async def send_bulk_emails(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_content: str,
        campaign_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            logger.info(f"Sending bulk emails to {len(recipients)} recipients")
            
            results = {
                'success': [],
                'failed': [],
                'campaign_id': campaign_id
            }

            for i in range(0, len(recipients), self.batch_size):
                batch = recipients[i:i + self.batch_size]
                batch_results = await self._send_batch(batch, subject, html_content, campaign_id)
                
                results['success'].extend(batch_results['success'])
                results['failed'].extend(batch_results['failed'])

            logger.info(f"Bulk email sending completed. Success: {len(results['success'])}, Failed: {len(results['failed'])}")
            return results

        except Exception as e:
            logger.error(f"Error in bulk email sending: {str(e)}")
            raise

    async def _send_batch(
        self,
        recipients: List[Dict[str, str]],
        subject: str,
        html_content: str,
        campaign_id: Optional[str]
    ) -> Dict[str, Any]:
        results = {'success': [], 'failed': []}
        
        for recipient in recipients:
            try:
                email = sib_api_v3_sdk.SendSmtpEmail(
                    to=[{'email': recipient['email'], 'name': recipient.get('name', '')}],
                    subject=subject,
                    html_content=html_content,
                    headers={'X-Campaign-ID': campaign_id} if campaign_id else None
                )

                response = self.api_instance.send_transac_email(email)
                results['success'].append({
                    'email': recipient['email'],
                    'message_id': response.message_id
                })

            except ApiException as e:
                logger.error(f"Failed to send email to {recipient['email']}: {str(e)}")
                results['failed'].append({
                    'email': recipient['email'],
                    'error': str(e)
                })

        return results

    async def create_campaign(
        self,
        name: str,
        subject: str,
        html_content: str
    ) -> Dict[str, Any]:
        try:
            campaign_api = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(self.configuration))
            
            campaign = sib_api_v3_sdk.CreateEmailCampaign(
                name=name,
                subject=subject,
                html_content=html_content,
                sender={'name': settings.EMAIL_SENDER_NAME, 'email': settings.EMAIL_SENDER_EMAIL},
                recipients={'listIds': []},  # Required by API, can be empty if sending to all
                inline_image_activation=True  # Embed images in the email
            )

            response = campaign_api.create_email_campaign(campaign)
            return {
                'campaign_id': response.id,
                'name': name,
                'status': 'created'
            }

        except ApiException as e:
            logger.error(f"Failed to create campaign: {str(e)}")
            raise

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        try:
            campaign_api = sib_api_v3_sdk.EmailCampaignsApi(sib_api_v3_sdk.ApiClient(self.configuration))
            stats = campaign_api.get_email_campaign(campaign_id)
            
            return {
                'campaign_id': campaign_id,
                'sent': stats.statistics.sent,
                'delivered': stats.statistics.delivered,
                'opened': stats.statistics.opened,
                'clicked': stats.statistics.clicked,
                'bounced': stats.statistics.bounced
            }

        except ApiException as e:
            logger.error(f"Failed to get campaign stats: {str(e)}")
            raise

    async def validate_email_addresses(self, emails: List[str]) -> Dict[str, List[str]]:
        try:
            results = {'valid': [], 'invalid': []}
            
            for email in emails:
                try:
                    self.contacts_api.get_contact_info(email)
                    results['valid'].append(email)
                except ApiException:
                    results['invalid'].append(email)

            return results

        except Exception as e:
            logger.error(f"Error in email validation: {str(e)}")
            raise 