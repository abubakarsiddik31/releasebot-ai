from typing import Optional, Dict, List
from github import Github, GithubException
from github.Repository import Repository
from github.PaginatedList import PaginatedList
from github.Commit import Commit
from github.Release import Release

from src.config.settings import settings
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff, rate_limit

logger = setup_logger(__name__, "github.log")

class GitHubService:
    def __init__(self):
        self.github = Github(settings.GITHUB_TOKEN)
        self.repo: Optional[Repository] = None
        self._initialize_repo()

    def _initialize_repo(self) -> None:
        try:
            self.repo = self.github.get_repo(settings.GITHUB_REPO)
            logger.info(f"Successfully connected to repository: {settings.GITHUB_REPO}")
        except GithubException as e:
            logger.error(f"Failed to initialize repository: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_latest_release(self) -> Optional[Release]:
        try:
            return self.repo.get_latest_release()
        except GithubException as e:
            if e.status == 404:
                logger.info("No releases found in repository")
                return None
            logger.error(f"Error getting latest release: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_release_by_tag(self, tag: str) -> Optional[Release]:
        try:
            return self.repo.get_release(tag)
        except GithubException as e:
            if e.status == 404:
                logger.info(f"Release not found: {tag}")
                return None
            logger.error(f"Error getting release by tag: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_commits_between_releases(
        self, start_tag: str, end_tag: str
    ) -> List[Commit]:
        try:
            start_release = await self.get_release_by_tag(start_tag)
            end_release = await self.get_release_by_tag(end_tag)

            if not start_release or not end_release:
                raise ValueError("One or both releases not found")

            return list(self.repo.compare(start_release.tag_name, end_release.tag_name).commits)
        except GithubException as e:
            logger.error(f"Error getting commits between releases: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_release_notes(self, release: Release) -> str:
        try:
            return release.body or ""
        except GithubException as e:
            logger.error(f"Error getting release notes: {str(e)}")
            raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_changelog_content(self, release: Release) -> Dict:
        try:
            return {
                "tag_name": release.tag_name,
                "name": release.title,
                "body": release.body,
                "created_at": release.created_at,
                "published_at": release.published_at,
                "prerelease": release.prerelease,
                "assets": [
                    {
                        "name": asset.name,
                        "size": asset.size,
                        "download_count": asset.download_count
                    }
                    for asset in release.get_assets()
                ]
            }
        except GithubException as e:
            logger.error(f"Error getting changelog content: {str(e)}")
            raise

    def __del__(self):
        if hasattr(self, "github"):
            self.github.close() 