
from app.agents.complaint_agent import ComplaintIntelligenceAgent
from app.config import get_settings

def verify():
    settings = get_settings()
    print(f"API Key present: {bool(settings.gemini_api_key)}")
    if settings.gemini_api_key:
        print(f"API Key length: {len(settings.gemini_api_key)}")
    
    agent = ComplaintIntelligenceAgent()
    if agent.model is None:
        print("Model is NONE - fallback mode active.")
    else:
        print("Model is initialized.")

    # Test with a high-impact complaint
    subject = "EXTREMELY URGENT: DATA LEAK AND SYSTEM CRASH"
    body = "Our entire customer database seems to be exposed and the main dashboard is offline. We are losing $50k per hour and our legal team is involved. CHURN RISK IS 100% IF NOT FIXED IN 1 HOUR."
    
    print("\nRunning analysis...")
    analysis = agent.analyze_complaint(subject, body, "cto@majorclient.com")
    
    print("\nAnalysis Results:")
    print(f"Title: {analysis.title}")
    print(f"Type: {analysis.complaint_type}")
    print(f"Priority: {analysis.priority}")
    print(f"Sentiment: {analysis.sentiment_score}")
    print(f"Churn Risk: {analysis.churn_risk}")
    print(f"Executive Summary: {analysis.executive_summary}")
    
    # Heuristic to detect if it's default:
    # Default priority is 'medium', default churn is 0.3, default sentiment for non-AI is -0.3
    if analysis.priority == "medium" and analysis.churn_risk == 0.3:
        print("\nWARNING: Results match default fallback values exactly. AI might not be working.")
    else:
        print("\nSUCCESS: AI seems to be producing custom results!")

if __name__ == "__main__":
    verify()
