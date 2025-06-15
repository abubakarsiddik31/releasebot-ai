from typing import Dict, Any, ClassVar, List, Optional
from langchain.tools import BaseTool
from pydantic import Field
from src.utils.ai_client import OpenRouterClient
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "content_generator.log")

class ContentGenerator(BaseTool):
    name: ClassVar[str] = "content_generator"
    description: ClassVar[str] = "Generates email content for releases"
    ai_client: Optional[OpenRouterClient] = Field(default=None)
    
    def __init__(self):
        super().__init__()
        self.ai_client = OpenRouterClient()

    @log_execution_time(logger)
    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["analyzed_changes"] or not state["feature_summary"]:
                return {"errors": ["Missing analyzed changes or feature summary"]}

            subject = await self._generate_subject(state["feature_summary"])
            content = await self._generate_content(
                state["analyzed_changes"],
                state["feature_summary"]
            )

            return {
                "email_subject": subject,
                "email_content": content
            }

        except Exception as e:
            logger.error(f"Error in content generation: {str(e)}")
            return {"errors": [str(e)]}

    @retry_with_backoff()
    async def _generate_subject(self, summary: str) -> str:
        prompt = f"""Create a concise email subject line for this release:
        {summary}

        Keep it under 60 characters and make it engaging.
        """

        return await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

    @retry_with_backoff()
    async def _generate_content(self, changes: Dict[str, List[str]], summary: str) -> str:
        prompt = f"""Create an engaging email content for this release:

        Summary:
        {summary}

        Changes:
        {changes}

        Include:
        1. Brief introduction
        2. Key highlights
        3. Detailed changes
        4. Call to action
        """

        content = await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

        return self._format_html_content(content)

    def _format_html_content(self, content: str) -> str:
        return f"""
        <html>
            <body>
                {content}
            </body>
        </html>
        """

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 