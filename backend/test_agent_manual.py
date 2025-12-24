
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from app.agents.complaint_agent import ComplaintIntelligenceAgent
from app.config import get_settings

def test_agent():
    print("Testing Complaint Intelligence Agent...")
    settings = get_settings()
    
    if not settings.gemini_api_key:
        print("ERROR: GEMINI_API_KEY not found in settings!")
        return

    agent = ComplaintIntelligenceAgent()
    
    subject = "Urgent: System Down"
    body = "Our production server is unreachable since 2 AM. We are losing money every minute. Fix this immediately!"
    sender = "admin@victim-company.com"

    print(f"\nAnalyzing Complaint:\nSubject: {subject}\nBody: {body}\n")
    
    try:
        analysis = agent.analyze_complaint(subject, body, sender)
        print("\n--- AI Analysis Result ---")
        print(f"Title: {analysis.title}")
        print(f"Priority: {analysis.priority}")
        print(f"Sentiment: {analysis.sentiment_score}")
        print(f"Churn Risk: {analysis.churn_risk}")
        print(f"Summary: {analysis.executive_summary}")
        print("--------------------------")
        
        if analysis.sentiment_score < 0:
            print("\nSUCCESS: Agent correctly identified negative sentiment.")
        else:
            print("\nWARNING: Agent did not identify negative sentiment.")
            
    except Exception as e:
        print(f"\nERROR: Agent failed with exception: {e}")

if __name__ == "__main__":
    test_agent()
