import streamlit as st
import asyncio

from src.services.github_service import GitHubService
from src.utils.logger import setup_logger
from src.config.settings import settings

logger = setup_logger(__name__, "github.log")

st.set_page_config(page_title="GitHub Releases", page_icon="🚀")
st.title("GitHub Releases")

# Check GitHub configuration
def check_github_config():
    if not settings.GITHUB_TOKEN:
        st.error("⚠️ GitHub Token is not configured. Please set the GITHUB_TOKEN in your environment variables.")
        st.info("To get a GitHub token:")
        st.markdown("""
        1. Go to GitHub Settings → Developer Settings → Personal Access Tokens → Tokens (classic)
        2. Generate a new token with `repo` scope
        3. Add the token to your environment variables as `GITHUB_TOKEN`
        """)
        return False
        
    if not settings.GITHUB_REPO:
        st.error("⚠️ GitHub Repository is not configured. Please set the GITHUB_REPO in your environment variables.")
        st.info("Set GITHUB_REPO in the format 'username/repository'")
        return False
    
    return True

def serialize_datetime(dt):
    """Convert datetime to string if it exists, otherwise return None."""
    return dt.isoformat() if dt else None

async def fetch_release_data():
    """Async function to fetch release data from GitHub."""
    try:
        github_service = GitHubService()
        latest_release = await github_service.get_latest_release()
        if latest_release:
            return await github_service.get_changelog_content(latest_release)
        return None
    except Exception as e:
        logger.error(f"Error fetching latest release: {str(e)}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_latest_release():
    """Cached function to get the latest release data."""
    try:
        release_data = asyncio.run(fetch_release_data())
        if release_data:
            # Convert datetime objects to ISO format strings
            return {
                "tag_name": release_data["tag_name"],
                "name": release_data["name"],
                "body": release_data["body"],
                "created_at": serialize_datetime(release_data["created_at"]),
                "published_at": serialize_datetime(release_data["published_at"]),
                "prerelease": release_data["prerelease"],
                "assets": [
                    {
                        "name": asset["name"],
                        "size": asset["size"],
                        "download_count": asset["download_count"]
                    }
                    for asset in release_data["assets"]
                ]
            }
        return None
    except Exception as e:
        logger.error(f"Error processing release data: {str(e)}")
        return None

# Main content
if not check_github_config():
    st.stop()

try:
    with st.status("Fetching latest release..."):
        latest_release = get_latest_release()
    
    if latest_release:
        st.header(f"Latest Release: {latest_release['name']}")
        
        # Release metadata
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Tag", latest_release['tag_name'])
        with col2:
            published_date = latest_release['published_at'][:10] if latest_release['published_at'] else "Not published"
            st.metric("Published", published_date)
        with col3:
            release_type = "Pre-release" if latest_release['prerelease'] else "Stable Release"
            st.metric("Type", release_type)
        
        # Release notes
        st.subheader("Release Notes")
        if latest_release['body']:
            st.markdown(latest_release['body'])
        else:
            st.info("No release notes available.")
        
        # Assets
        if latest_release['assets']:
            st.subheader("Assets")
            for asset in latest_release['assets']:
                with st.expander(f"📎 {asset['name']}"):
                    st.text(f"Size: {asset['size']:,} bytes")
                    st.text(f"Downloads: {asset['download_count']:,}")
    else:
        st.info("No releases found for this repository.")
        
except Exception as e:
    st.error(f"An error occurred while fetching release information: {str(e)}")
    logger.error(f"Error in Streamlit app: {str(e)}")
