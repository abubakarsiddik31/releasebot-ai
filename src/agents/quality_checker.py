from typing import Dict, Any, List, ClassVar, Tuple, Optional
import json
from langchain.tools import BaseTool
from pydantic import Field

from src.utils.ai_client import OpenRouterClient
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "quality_checker.log")

class QualityChecker(BaseTool):
    name: ClassVar[str] = "quality_checker"
    description: ClassVar[str] = "Checks email content quality"
    ai_client: Optional[OpenRouterClient] = Field(default=None)
    quality_threshold: float = 0.7
    spam_trigger_words: List[str] = Field(default_factory=list)
    
    def __init__(self):
        super().__init__()
        self.ai_client = OpenRouterClient()
        self.spam_trigger_words = [
            "free", "guarantee", "winner", "congratulations",
            "urgent", "act now", "limited time", "exclusive"
        ]

    @log_execution_time(logger)
    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["email_content"] or not state["email_subject"]:
                return {"errors": ["Missing email content or subject"]}

            quality_score, feedback = await self._evaluate_content(
                state["email_content"],
                state["email_subject"]
            )

            return {
                "quality_score": quality_score,
                "quality_feedback": feedback,
                "needs_revision": quality_score < self.quality_threshold
            }

        except Exception as e:
            logger.error(f"Error in quality check: {str(e)}")
            return {"errors": [str(e)]}

    @retry_with_backoff()
    async def _evaluate_content(self, content: str, subject: str) -> Tuple[float, List[str]]:
        prompt = f"""Evaluate this email content and subject for quality:

        Subject: {subject}
        Content: {content}

        Consider:
        1. Clarity and readability
        2. Technical accuracy
        3. Professional tone
        4. Mobile responsiveness
        5. Spam triggers

        Return a JSON object with:
        - score: float between 0 and 1
        - feedback: list of specific improvements
        """

        response = await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a content quality expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = json.loads(response)
        return result["score"], result["feedback"]

    def _check_spam_triggers(self, content: str) -> List[str]:
        found_triggers = []
        content_lower = content.lower()
        
        for trigger in self.spam_trigger_words:
            if trigger in content_lower:
                found_triggers.append(trigger)
                
        return found_triggers

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 