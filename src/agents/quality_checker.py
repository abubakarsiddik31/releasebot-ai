from typing import Dict, Any, List
from src.utils.logger import get_logger
from src.utils.ai_client import get_ai_client
from src.config.settings import settings

logger = get_logger(__name__)

class QualityChecker:
    def __init__(self):
        self.ai_client = get_ai_client()
        self.quality_threshold = 7.0
        self.spam_trigger_words = [
            "free", "guarantee", "winner", "winner", "won", "win", "won", "winning",
            "winner", "won", "win", "winning", "winner", "won", "win", "winning",
            "winner", "won", "win", "winning", "winner", "won", "win", "winning"
        ]

    async def check_quality(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Starting quality check for release {state.get('release_tag')}")
            
            if not state.get('email_content') or not state.get('email_subject'):
                raise ValueError("Missing email content or subject for quality check")

            quality_score, feedback = await self._evaluate_content(
                state['email_subject'],
                state['email_content'],
                state.get('analyzed_changes', {})
            )

            state['quality_score'] = quality_score
            state['quality_feedback'] = feedback
            state['approved'] = quality_score >= self.quality_threshold

            if not state['approved']:
                logger.warning(f"Content rejected with score {quality_score}: {feedback}")
            else:
                logger.info(f"Content approved with score {quality_score}")

            return state

        except Exception as e:
            logger.error(f"Error in quality check: {str(e)}")
            state['errors'].append(f"Quality check failed: {str(e)}")
            state['approved'] = False
            return state

    async def _evaluate_content(
        self,
        subject: str,
        content: str,
        analyzed_changes: Dict[str, Any]
    ) -> tuple[float, str]:
        prompt = f"""Evaluate the following email content for quality and accuracy:

Subject: {subject}

Content:
{content}

Original Changes:
{analyzed_changes}

Evaluate the content based on:
1. Technical accuracy compared to original changes
2. Professional tone and clarity
3. Spam trigger words and marketing compliance
4. Completeness of information
5. User benefit focus

Provide a score from 1-10 and specific feedback for improvement.
Format: SCORE: [number]\\nFEEDBACK: [detailed feedback]"""

        response = await self.ai_client.get_completion(prompt)
        
        try:
            score_line = response.split('\n')[0]
            score = float(score_line.split(':')[1].strip())
            feedback = response.split('FEEDBACK:')[1].strip()
            
            if score < 1 or score > 10:
                score = 5.0
                feedback = "Invalid score format. Defaulting to neutral score."
                
            return score, feedback
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return 5.0, "Error in quality evaluation. Manual review required."

    def _check_spam_triggers(self, content: str) -> List[str]:
        found_triggers = []
        content_lower = content.lower()
        
        for word in self.spam_trigger_words:
            if word in content_lower:
                found_triggers.append(word)
                
        return found_triggers 