from typing import Dict, Any, List, ClassVar, Optional
import json
from langchain.tools import BaseTool
from pydantic import Field

from src.utils.ai_client import OpenRouterClient
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "change_analyzer.log")

class ChangeAnalyzer(BaseTool):
    name: ClassVar[str] = "change_analyzer"
    description: ClassVar[str] = "Analyzes and categorizes release changes"
    ai_client: Optional[OpenRouterClient] = Field(default=None)
    categories: Dict[str, str] = Field(
        default_factory=lambda: {
            "features": "New Features",
            "fixes": "Bug Fixes",
            "improvements": "Improvements",
            "breaking": "Breaking Changes"
        }
    )
    
    def __init__(self):
        super().__init__()
        self.ai_client = OpenRouterClient()

    @log_execution_time(logger)
    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["release_data"]:
                return {"errors": ["No release data available"]}

            changes = await self._analyze_changes(state["changelog"])
            summary = await self._generate_summary(changes)

            return {
                "analyzed_changes": changes,
                "feature_summary": summary
            }

        except Exception as e:
            logger.error(f"Error in change analysis: {str(e)}")
            return {"errors": [str(e)]}
        finally:
            await self.ai_client.close()

    @retry_with_backoff()
    async def _analyze_changes(self, changelog: str) -> Dict[str, List[str]]:
        prompt = f"""Analyze these release changes and categorize them:
        - New Features (user-facing functionality)
        - Bug Fixes (problem resolutions)
        - Improvements (enhancements to existing features)
        - Breaking Changes (backward compatibility issues)

        Changes:
        {changelog}

        Return a JSON object with categories as keys and lists of changes as values.
        """

        response = await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a technical change analyzer."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response)

    @retry_with_backoff()
    async def _generate_summary(self, changes: Dict[str, List[str]]) -> str:
        prompt = f"""Create a concise summary of these changes, focusing on user impact:
        {changes}

        Keep it brief but informative, highlighting the most important changes.
        """

        return await self.ai_client.generate_completion(
            messages=[
                {"role": "system", "content": "You are a technical writer."},
                {"role": "user", "content": prompt}
            ]
        )

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 