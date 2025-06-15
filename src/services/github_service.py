from typing import Optional, Dict, List
from github import Github, GithubException
from github.Repository import Repository
from github.Commit import Commit
from github.GitRelease import GitRelease as Release

from src.config.settings import settings
from src.utils.logger import setup_logger, log_execution_time
from src.utils.helpers import retry_with_backoff, rate_limit

logger = setup_logger(__name__, "github.log")

class GitHubService:
    def __init__(self):
        self._validate_config()
        self.github = Github(settings.GITHUB_TOKEN)
        self.repo: Optional[Repository] = None
        self._initialize_repo()

    def _validate_config(self) -> None:
        """Validate GitHub configuration settings."""
        if not settings.GITHUB_TOKEN:
            raise ValueError("GitHub token is not configured. Please set GITHUB_TOKEN in environment variables.")
        
        if not settings.GITHUB_REPO:
            raise ValueError("GitHub repository is not configured. Please set GITHUB_REPO in environment variables.")
        
        if "/" not in settings.GITHUB_REPO:
            raise ValueError("Invalid GITHUB_REPO format. Must be in format 'username/repository'.")

    async def close(self) -> None:
        """Close the GitHub client connection."""
        if hasattr(self, 'github') and self.github:
            self.github.close()

    def _initialize_repo(self) -> None:
        """Initialize GitHub repository connection with detailed error handling."""
        try:
            self.repo = self.github.get_repo(settings.GITHUB_REPO)
            # Test the connection by accessing a basic property
            _ = self.repo.full_name
            logger.info(f"Successfully connected to repository: {settings.GITHUB_REPO}")
        except GithubException as e:
            if e.status == 404:
                logger.error(f"Repository not found: {settings.GITHUB_REPO}. Please check if the repository exists and you have access to it.")
                raise ValueError(f"Repository not found: {settings.GITHUB_REPO}. Please verify the repository name and your access permissions.") from e
            elif e.status == 401:
                logger.error("Invalid GitHub token. Please check your GITHUB_TOKEN.")
                raise ValueError("Invalid GitHub token. Please verify your GITHUB_TOKEN.") from e
            elif e.status == 403:
                logger.error("Access forbidden. Please check your GitHub token permissions.")
                raise ValueError("Access forbidden. Please verify your GitHub token has the required permissions.") from e
            else:
                logger.error(f"Failed to initialize repository: {str(e)}")
                raise

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_latest_release(self) -> Optional[Release]:
        """Get the latest release from the repository with detailed error handling."""
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
            return self.repo.get_latest_release()
        except GithubException as e:
            if e.status == 404:
                logger.info(f"No releases found in repository {settings.GITHUB_REPO}")
                return None
            elif e.status == 401:
                logger.error("Invalid GitHub token while fetching release.")
                raise ValueError("Invalid GitHub token. Please verify your GITHUB_TOKEN.") from e
            elif e.status == 403:
                logger.error("Access forbidden while fetching release.")
                raise ValueError("Access forbidden. Please verify your GitHub token has the required permissions.") from e
            else:
                logger.error(f"Error getting latest release: {str(e)}")
                raise ValueError(f"Failed to fetch latest release: {str(e)}") from e

    @retry_with_backoff(max_retries=3, exceptions=(GithubException,))
    @rate_limit(calls=5000, period=3600)
    @log_execution_time(logger)
    async def get_release_by_tag(self, tag: str) -> Optional[Release]:
        try:
            if not self.repo:
                raise ValueError("Repository not initialized")
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
            if not self.repo:
                raise ValueError("Repository not initialized")
                
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
    async def get_changelog_content(self, release: Optional[Release]) -> Optional[Dict]:
        try:
            if not release:
                return None
            return {
                "tag_name": release.tag_name,
                "name": release.title or release.tag_name,  # Fallback to tag_name if title is None
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