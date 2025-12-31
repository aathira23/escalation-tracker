"""
Complaint Intelligence Agent
Uses Google Gemini to analyze raw complaints and extract structured information.
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
class ComplaintAnalysis:
    """Structured output from complaint analysis."""
    title: str
    description: str
    executive_summary: str
    sender_name: Optional[str]
    company_name: Optional[str]
    complaint_type: str
    priority: str  # low, medium, high, critical
    sentiment_score: float  # -1.0 to 1.0
    churn_risk: float  # 0.0 to 1.0
    key_issues: List[str]
    resolution_suggestions: List[str]


class ComplaintIntelligenceAgent:
    """
    AI agent that processes raw email complaints using Google Gemini.
    
    Performs:
    - Entity extraction (sender, company, issue title)
    - Description cleanup
    - Executive summary generation
    - Sentiment analysis
    - Complaint type classification
    - Priority determination
    - Churn risk assessment
    """
    
    SYSTEM_PROMPT = """You are an expert AI complaint analyst and customer success strategist.
Your job is to analyze client complaint emails and extract structured information that helps managers and resolvers take immediate, effective action.

CRITICAL INSTRUCTION: Your output MUST be highly customized to the specific email. 
1. **Title**: A crisp, professional title summarizing the core issue (max 100 chars).
2. **Description**: A clean, structured version of the complaint, removing noise (like signatures or legalese) while preserving all critical technical or emotional details.
3. **Executive Summary**: A punchy 2-3 sentence summary explaining exactly what went wrong and what the immediate impact is. Use specific dates, names, or IDs mentioned in the email.
4. **Sender Name**: Full name of the complainant (if available).
5. **Company Name**: The client's company name.
6. **Complaint Type**: Categorize accurately as: billing, technical, service, product, delivery, communication, or other.
7. **Priority**: Determine based on business impact, SLA risk, and emotional intensity. Valid values: low, medium, high, critical.
8. **Sentiment Score**: A precise float from -1.0 (extremely frustrated/angry) to 1.0 (positive/praise).
9. **Churn Risk**: An assessment of how likely the client is to leave based on the tone and severity (0.0 to 1.0).
10. **Key Issues**: A list of specific, non-overlapping points of failure or concern mentioned in the text.
11. **Resolution Suggestions**: Provide 3-4 HIGHLY SPECIFIC, ACTIONABLE, and CUSTOMIZED steps. 
    - MANDATORY: Every suggestion must reference at least one specific detail from the email (e.g., "Check status of Order #123", "Verify Refund for transaction dated Oct 12", "Contact [Sender Name] at [Sender Phone]").
    - FORBIDDEN: Do not use generic phrases like "Investigate the root cause", "Contact the client", or "Verify the technical log" without adding specific context from the email.

Respond ONLY with valid JSON in this exact format:
{
    "title": "string",
    "description": "string",
    "executive_summary": "string",
    "sender_name": "string or null",
    "company_name": "string or null",
    "complaint_type": "string",
    "priority": "low|medium|high|critical",
    "sentiment_score": float,
    "churn_risk": float,
    "key_issues": ["string"],
    "resolution_suggestions": ["string"]
}"""
    
    def __init__(self):
        """Initialize the Gemini model."""
        if settings.gemini_api_key and genai:
            try:
                genai.configure(api_key=settings.gemini_api_key)
                # Use gemini-2.0-flash - confirmed working in this environment
                self.model = genai.GenerativeModel('gemini-2.0-flash')
            except Exception as e:
                print(f"Error initializing Gemini: {e}")
                self.model = None
        else:
            self.model = None
    
    def analyze_complaint(self, email_subject: str, email_body: str, sender_email: str) -> ComplaintAnalysis:
        """
        Analyze a raw complaint email and extract structured information.
        
        Args:
            email_subject: Subject line of the email
            email_body: Body content of the email
            sender_email: Sender's email address
            
        Returns:
            ComplaintAnalysis dataclass with extracted information
        """
        if not self.model:
            # Return default analysis if no API key
            return self._default_analysis(email_subject, email_body)
        
        prompt = f"""Analyze this complaint email:

From: {sender_email}
Subject: {email_subject}

Body:
{email_body}

Extract the structured information as specified."""
        
        try:
            response = self.model.generate_content(
                self.SYSTEM_PROMPT + "\n\n" + prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=1024,
                )
            )
            
            # Parse JSON response
            response_text = response.text.strip()
            # Handle potential markdown code blocks
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            data = json.loads(response_text)
            
            return ComplaintAnalysis(
                title=data.get("title", email_subject)[:500],
                description=data.get("description", email_body),
                executive_summary=data.get("executive_summary", ""),
                sender_name=data.get("sender_name"),
                company_name=data.get("company_name"),
                complaint_type=data.get("complaint_type", "other"),
                priority=data.get("priority", "medium"),
                sentiment_score=float(data.get("sentiment_score", 0.0)),
                churn_risk=float(data.get("churn_risk", 0.3)),
                key_issues=data.get("key_issues", []),
                resolution_suggestions=data.get("resolution_suggestions", [])
            )
            
        except Exception as e:
            print(f"Error analyzing complaint with AI: {e}")
            return self._default_analysis(email_subject, email_body)
    
    def _default_analysis(self, subject: str, body: str) -> ComplaintAnalysis:
        """Return smart fallback analysis when AI is unavailable."""
        import re
        content = (subject + " " + body)
        content_lower = content.lower()
        
        # Smart extraction of potential entities
        # Extract things that look like IDs, transaction numbers, or dates
        potential_ids = re.findall(r'#\d+|[A-Z]{2,}-\d+|\b\d{6,}\b', content)
        potential_dates = re.findall(r'\d{1,2}/\d{1,2}/\d{2,4}|\d{1,2}-\d{1,2}-\d{2,4}', content)

        
        id_str = f" ({potential_ids[0]})" if potential_ids else ""
        date_str = f" mentioned on {potential_dates[0]}" if potential_dates else ""
        
        complaint_type = "other"
        resolution = [
            f"Acknowledge the specific issue{id_str} with a personalized email response within 4 hours.",
            f"Trace the internal timeline of events starting from the trigger{date_str}."
        ]
        
        priority = "medium"
        churn_risk = 0.3
        
        if any(w in content_lower for w in ["billing", "invoice", "charge", "refund", "payment"]):
            complaint_type = "billing"
            priority = "high"
            resolution.append(f"Audit the billing gateway for any duplicate entries matching {id_str or 'the transactions'}.")
            resolution.append("Verify the internal ledger against the client's reported discrepancy.")
        elif any(w in content_lower for w in ["api", "performance", "technical", "error", "bug", "down", "endpoint"]):
            complaint_type = "technical"
            priority = "high"
            # Extract potential endpoint
            endpoints = re.findall(r'/[a-z0-9/_\-\?]+', content_lower)
            endpoint_str = f" for {endpoints[0]}" if endpoints else ""
            resolution.append(f"Isolate system logs{endpoint_str} for the specific error pattern{id_str}.")
            resolution.append("Assign to an engineer to verify the environmental state at the time of failure.")
        elif any(w in content_lower for w in ["urgent", "immediately", "asap", "disaster", "critical", "stop"]):
            priority = "critical"
            churn_risk = 0.7
            resolution.insert(0, f"EMERGENCY PROTOCOL: Escalate {subject[:50]} to senior management immediately.")
            
        return ComplaintAnalysis(
            title=subject[:500] if subject else "Untitled Complaint",
            description=body,
            executive_summary=f"Automated smart-analysis: This appears to be a {complaint_type} issue needing immediate review.",
            sender_name=None,
            company_name=None,
            complaint_type=complaint_type,
            priority=priority,
            sentiment_score=-0.4,
            churn_risk=churn_risk,
            key_issues=[f"Specific context observed: {', '.join(potential_ids[:2] + potential_dates[:1]) or 'General complaint content'}"],
            resolution_suggestions=resolution
        )
