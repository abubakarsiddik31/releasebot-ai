from typing import Dict, Any, List
import json

from src.utils.ai_client import OpenRouterClient
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "change_analyzer.log")

class ChangeAnalyzer:
    """Change analyzer agent"""
    def __init__(self):
        self.ai_client = OpenRouterClient()
        self.categories = {
            "features": "New Features",
            "fixes": "Bug Fixes",
            "improvements": "Improvements",
            "breaking": "Breaking Changes"
        }

    @log_execution_time(logger)
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not state["release_data"]:
                state["errors"].append("No release data available")
                return state

            changes = await self._analyze_changes(state["changelog"])
            summary = await self._generate_summary(changes)

            state["analyzed_changes"] = changes
            state["feature_summary"] = summary
            return state

        except Exception as e:
            logger.error(f"Error in change analysis: {str(e)}")
            state["errors"].append(str(e))
            return state
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