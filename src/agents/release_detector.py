from typing import Dict, Any, Optional
from datetime import datetime

from src.services.github_service import GitHubService
from src.services.database_service import get_db
from src.models.database import ReleasesProcessed
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff

logger = setup_logger(__name__, "release_detector.log")

class ReleaseDetector:
    def __init__(self):
        self.github_service = GitHubService()

    @log_execution_time(logger)
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if state["manual_trigger"]:
                release = await self.github_service.get_release_by_tag(state["release_tag"])
            else:
                release = await self.github_service.get_latest_release()

            if not release:
                state["errors"].append("No release found")
                return state

            if release.prerelease:
                state["errors"].append("Skipping pre-release")
                return state

            with get_db() as db:
                existing = db.query(ReleasesProcessed).filter_by(
                    release_tag=release.tag_name
                ).first()

                if existing:
                    state["errors"].append(f"Release {release.tag_name} already processed")
                    return state

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
                db.commit()

                state["release_data"] = release_data
                state["changelog"] = changelog["body"]
                return state

        except Exception as e:
            logger.error(f"Error in release detection: {str(e)}")
            state["errors"].append(str(e))
            return state 