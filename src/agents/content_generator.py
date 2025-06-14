from typing import Dict, Any
from src.utils.ai_client import OpenRouterClient
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "content_generator.log")

class ContentGenerator:
    def __init__(self):
        self.ai_client = OpenRouterClient()

    @log_execution_time(logger)
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["analyzed_changes"] or not state["feature_summary"]:
                state["errors"].append("No analyzed changes available")
                return state

            subject = await self._generate_subject(state["feature_summary"])
            content = await self._generate_content(
                state["analyzed_changes"],
                state["feature_summary"]
            )

            state["email_subject"] = subject
            state["email_content"] = self._format_html_content(content)
            return state

        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            state["errors"].append(str(e))
            return state
        finally:
            await self.ai_client.close()

    @retry_with_backoff()
    async def _generate_subject(self, summary: str) -> str:
        prompt = f"""Create an engaging email subject line for this release summary:
        {summary}

        Keep it concise and compelling, focusing on the most impactful changes.
        """

        return await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are an email subject line expert."},
                {"role": "user", "content": prompt}
            ]
        )

    @retry_with_backoff()
    async def _generate_content(self, changes: Dict[str, list], summary: str) -> str:
        prompt = f"""Create a professional email content for this release:
        Summary: {summary}
        Changes: {changes}

        Include:
        1. Brief introduction
        2. Key changes and their benefits
        3. Call to action
        Keep it concise and mobile-friendly.
        """

        return await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a technical content writer."},
                {"role": "user", "content": prompt}
            ]
        )

    def _format_html_content(self, content: str) -> str:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .content {{ padding: 20px 0; }}
                .footer {{ font-size: 12px; color: #666; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="content">
                    {content}
                </div>
                <div class="footer">
                    <p>This is an automated release notification.</p>
                </div>
            </div>
        </body>
        </html>
        """ 