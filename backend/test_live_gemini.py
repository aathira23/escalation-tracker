
import asyncio
import os
from app.agents.complaint_agent import ComplaintIntelligenceAgent
from app.config import get_settings

async def test_live_gemini():
    settings = get_settings()
    print(f"API Key Length: {len(settings.gemini_api_key)}")
    
    import google.generativeai as genai
    agent = ComplaintIntelligenceAgent()
    print(f"Agent model initialized: {bool(agent.model)}")
    if agent.model:
        print(f"Model type: {type(agent.model)}")
        print(f"Has GenerativeModel: {hasattr(genai, 'GenerativeModel')}")
        print(f"GenAI dir: {dir(genai)}")

    if not agent.model:
        print("FAILED: Agent could not initialize Gemini model. Is the key set correctly?")
        return

    print("Sending test request to Gemini...")
    try:
        analysis = agent.analyze_complaint(
            "Broken API endpoint /users/login",
            "The login endpoint returns 500 for all the requests since this morning. This is critical for our production.",
            "dev@client.com"
        )
        
        print("\n--- AI Results ---")
        print(f"Title: {analysis.title}")
        print(f"Priority: {analysis.priority}")
        print(f"Executive Summary: {analysis.executive_summary}")
        print(f"Resolution Suggestions: {analysis.resolution_suggestions}")
        
        # Check if it's the fallback or the real AI
        # Fallback executive summary is always "Automated analysis complete. Issue categorized..."
        if "Automated analysis complete" in analysis.executive_summary:
            print("\nWARNING: Still getting fallback responses. Check API connectivity or logs.")
        else:
            print("\nSUCCESS: Live Gemini AI response received!")
            
    except Exception as e:
        print(f"ERROR during AI analysis: {e}")

if __name__ == "__main__":
    asyncio.run(test_live_gemini())
