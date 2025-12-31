"""
Assignment Agent
Uses Google Gemini to recommend the best resolver for an escalation.
Note: This agent recommends only - managers make final assignment decisions.
"""
import json
from typing import Optional, List
from dataclasses import dataclass

try:
    import google.generativeai as genai
except ImportError:
    genai = None

from app.config import get_settings

settings = get_settings()


@dataclass
class AssignmentRecommendation:
    """Structured output from assignment recommendation."""
    recommended_user_id: str
    recommended_user_name: str
    reason: str
    confidence: float  # 0.0 to 1.0
    alternative_user_id: Optional[str]
    alternative_reason: Optional[str]


class AssignmentAgent:
    """
    AI agent that recommends the best resolver for an escalation.
    
    Analyzes:
    - Escalation type and priority
    - Resolver expertise tags
    - Current workload
    - Historical performance (future enhancement)
    
    Note: This agent provides recommendations only. Managers make final decisions.
    """
    
    SYSTEM_PROMPT = """You are an expert AI resource manager for an escalation team.
Your job is to recommend the best team member to resolve an escalation, ensuring the fastest resolution and highest customer satisfaction.

Decision Criteria:
1. **Expertise Synergy**: Match the escalation's technical or domain type with the resolver's expertise tags.
2. **Dynamic Workload**: Prioritize resolvers who have current capacity. Avoid overloading high-performers.
3. **Priority Alignment**: For critical or high-priority escalations, prefer resolvers with proven expertise in those areas, even if their workload is slightly higher.

You will receive:
- Escalation metadata (type, priority, title, description)
- A list of available resolvers with their specific expertise and current/max workload

Respond ONLY with valid JSON in this exact format:
{
    "recommended_user_id": "uuid string",
    "recommended_user_name": "string",
    "reason": "Provide a detailed, compelling justification explaining why this specific resolver is the best choice (citing expertise and workload balance).",
    "confidence": float (percentage of confidence from 0.0 to 1.0),
    "alternative_user_id": "uuid string or null",
    "alternative_reason": "Justification for a secondary option if the primary is unavailable."
}"""
    
    def __init__(self):
        """Initialize the Gemini model."""
        if settings.gemini_api_key and genai:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
    
    def recommend_assignment(
        self,
        escalation_title: str,
        escalation_description: str,
        escalation_type: str,
        escalation_priority: str,
        available_resolvers: List[dict]
    ) -> Optional[AssignmentRecommendation]:
        """
        Recommend the best resolver for an escalation.
        
        Args:
            escalation_title: Title of the escalation
            escalation_description: Description of the issue
            escalation_type: Type/category of complaint
            escalation_priority: Priority level
            available_resolvers: List of dicts with user info:
                {id, name, expertise_tags, current_workload, max_workload}
                
        Returns:
            AssignmentRecommendation or None if no suitable resolver found
        """
        if not self.model or not available_resolvers:
            return self._default_recommendation(available_resolvers)
        
        resolvers_text = "\n".join([
            f"- {r['name']} (ID: {r['id']})\n  Expertise: {', '.join(r.get('expertise_tags', []))}\n  Workload: {r['current_workload']}/{r['max_workload']}"
            for r in available_resolvers
        ])
        
        prompt = f"""Recommend the best resolver for this escalation:

**Escalation:**
- Title: {escalation_title}
- Type: {escalation_type}
- Priority: {escalation_priority}
- Description: {escalation_description[:500]}

**Available Resolvers:**
{resolvers_text}

Who should handle this escalation?"""
        
        try:
            response = self.model.generate_content(
                [{"role": "user", "parts": [self.SYSTEM_PROMPT + "\n\n" + prompt]}],
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=512,
                )
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            data = json.loads(response_text)
            
            return AssignmentRecommendation(
                recommended_user_id=data.get("recommended_user_id", ""),
                recommended_user_name=data.get("recommended_user_name", ""),
                reason=data.get("reason", "AI recommendation"),
                confidence=float(data.get("confidence", 0.7)),
                alternative_user_id=data.get("alternative_user_id"),
                alternative_reason=data.get("alternative_reason")
            )
            
        except Exception as e:
            print(f"Error getting AI recommendation: {e}")
            return self._default_recommendation(available_resolvers)
    
    def _default_recommendation(self, resolvers: List[dict]) -> Optional[AssignmentRecommendation]:
        """Return default recommendation (lowest workload) when AI is unavailable."""
        if not resolvers:
            return None
        
        # Sort by workload percentage (ascending)
        sorted_resolvers = sorted(
            resolvers,
            key=lambda r: r['current_workload'] / r['max_workload'] if r['max_workload'] > 0 else 0
        )
        
        best = sorted_resolvers[0]
        return AssignmentRecommendation(
            recommended_user_id=str(best['id']),
            recommended_user_name=best['name'],
            reason="Selected based on available capacity (AI recommendation unavailable)",
            confidence=0.5,
            alternative_user_id=str(sorted_resolvers[1]['id']) if len(sorted_resolvers) > 1 else None,
            alternative_reason="Second lowest workload" if len(sorted_resolvers) > 1 else None
        )
