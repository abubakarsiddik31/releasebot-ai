from typing import Dict, Any, ClassVar, Optional
from langchain.tools import BaseTool
from pydantic import Field
from sqlalchemy import select

from src.services.github_service import GitHubService
from src.services.database_service import get_db
from src.models.database import ReleasesProcessed
from src.utils.logger import setup_logger, log_execution_time

logger = setup_logger(__name__, "release_detector.log")

class ReleaseDetector(BaseTool):
    name: ClassVar[str] = "release_detector"
    description: ClassVar[str] = "Detects and processes new GitHub releases"
    github_service: Optional[GitHubService] = Field(default=None)
    
    def __init__(self):
        super().__init__()
        self.github_service = GitHubService()

    @log_execution_time(logger)
    async def _arun(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self.github_service:
                self.github_service = GitHubService()
                
            if state["manual_trigger"]:
                release = await self.github_service.get_release_by_tag(state["release_tag"])
            else:
                release = await self.github_service.get_latest_release()

            if not release:
                return {"errors": ["No release found"]}

            if release.prerelease:
                return {"errors": ["Skipping pre-release"]}

            async with get_db() as db:
                stmt = select(ReleasesProcessed).where(ReleasesProcessed.release_tag == release.tag_name)
                result = await db.execute(stmt)
                existing = result.scalar_one_or_none()

                if existing:
                    return {"errors": [f"Release {release.tag_name} already processed"]}

                changelog = await self.github_service.get_changelog_content(release)
                release_data = {
                    "tag_name": release.tag_name,
                    "name": release.title,
                    "body": release.body,
                    "created_at": release.created_at,
                    "published_at": release.published_at,
                    "prerelease": release.prerelease
                }

                new_release = ReleasesProcessed(
                    release_tag=release.tag_name,
                    status="processing"
                )
                db.add(new_release)
                await db.commit()

                return {
                    "release_data": release_data,
                    "changelog": changelog["body"]
                }

        except Exception as e:
            logger.error(f"Error in release detection: {str(e)}")
            return {"errors": [str(e)]}

    async def _run(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return await self._arun(state) 