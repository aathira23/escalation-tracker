"""
Complaint Intelligence Agent
Uses Google Gemini to analyze raw complaints and extract structured information.
"""
import json
from typing import Optional
from dataclasses import dataclass

import google.generativeai as genai

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
    key_issues: list[str]
    resolution_suggestions: list[str]


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
    
    SYSTEM_PROMPT = """You are an AI complaint analyst for an internal escalation tracking system.
Your job is to analyze client complaint emails and extract structured information.

For each email, you must extract:
1. **Title**: A concise title summarizing the complaint (max 100 chars)
2. **Description**: Clean, well-formatted description of the issue
3. **Executive Summary**: 2-3 sentence summary for managers
4. **Sender Name**: Name of the person who sent the email (if available)
5. **Company Name**: Company the sender works for (if identifiable)
6. **Complaint Type**: One of: billing, technical, service, product, delivery, communication, other
7. **Priority**: Based on urgency and impact: low, medium, high, critical
8. **Sentiment Score**: From -1.0 (very angry/frustrated) to 1.0 (positive/satisfied)
9. **Churn Risk**: Probability of client leaving (0.0 to 1.0)
10. **Key Issues**: List of main issues mentioned
11. **Resolution Suggestions**: List of 2-3 suggested action steps to resolve the issue

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
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
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
                [{"role": "user", "parts": [self.SYSTEM_PROMPT + "\n\n" + prompt]}],
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
        """Return default analysis when AI is unavailable."""
        subject_lower = subject.lower() if subject else ""
        content_lower = (subject + " " + body).lower()
        
        complaint_type = "other"
        resolution = ["Contact the client to acknowledge receipt", "Investigate the issue internally"]
        
        if "billing" in content_lower or "invoice" in content_lower or "charge" in content_lower:
            complaint_type = "billing"
            resolution.append("Verify invoice details in the billing system")
        elif "api" in content_lower or "performance" in content_lower or "technical" in content_lower:
            complaint_type = "technical"
            resolution.append("Check system logs for related errors")
        elif "feature" in content_lower or "product" in content_lower:
            complaint_type = "product"
            resolution.append("Review product roadmap and recent changes")
            
        return ComplaintAnalysis(
            title=subject[:500] if subject else "Untitled Complaint",
            description=body,
            executive_summary="Complaint received, pending detailed analysis.",
            sender_name=None,
            company_name=None,
            complaint_type=complaint_type,
            priority="medium",
            sentiment_score=-0.3,  # Assume slightly negative
            churn_risk=0.3,
            key_issues=[],
            resolution_suggestions=resolution
        )
