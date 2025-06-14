from typing import Dict, List, Optional
import httpx
from src.config.settings import settings
from src.utils.logger import setup_logger

logger = setup_logger(__name__, "ai_client.log")

class OpenRouterClient:
    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": "https://github.com/bakar31/releasebot-ai",
                "X-Title": "ReleaseBot AI"
            }
        )

    async def generate_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        response_format: Optional[Dict[str, str]] = None
    ) -> str:
        try:
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature
            }

            if max_tokens:
                payload["max_tokens"] = max_tokens
            if response_format:
                payload["response_format"] = response_format

            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"Error in AI completion: {str(e)}")
            raise

    async def close(self):
        await self.client.aclose() 