
import asyncio
import os
import re
from app.agents.complaint_agent import ComplaintIntelligenceAgent

def test_smart_fallback():
    print("\n--- Testing SMART FALLBACK (Offline Logic) ---")
    agent = ComplaintIntelligenceAgent()
    
    # Scenario 1: Billing with ID
    res1 = agent._default_analysis(
        "Billing error on Invoice #INV-2023-001",
        "I was charged twice on 12/25/2023 for the amount of $500. Please refund the duplicate charge INV-2023-001."
    )
    print(f"\nScenario: Billing with ID and Date")
    print(f"Suggestions: {res1.resolution_suggestions}")
    assert any("inv-2023" in s.lower() for s in res1.resolution_suggestions), "Should extract INV-2023"
    assert any("12/25/2023" in s for s in res1.resolution_suggestions), "Should extract date"
    
    # Scenario 2: Technical with Endpoint
    res2 = agent._default_analysis(
        "API Failure",
        "The endpoint /v1/users/login is returning 500 errors for user group 889911."
    )
    print(f"\nScenario: Technical with Endpoint and User ID")
    print(f"Suggestions: {res2.resolution_suggestions}")
    assert any("/v1/users/login" in s.lower() for s in res2.resolution_suggestions)
    assert any("889911" in s.lower() for s in res2.resolution_suggestions)
    
    print("\nSUCCESS: Smart Fallback is extracting and using specific details!")

async def test_live_customization():
    print("\n--- Testing LIVE AI CUSTOMIZATION (If Key Available) ---")
    agent = ComplaintIntelligenceAgent()
    if not agent.model:
        print("Skipping Live Test: No API Key")
        return

    print("Sending request to Gemini with specific details...")
    try:
        analysis = agent.analyze_complaint(
            "Broken payment for Order #ORD-998",
            "On 12/30/2023, I trying to pay for Order #ORD-998 but it failed at the /checkout/confirm screen. My name is Alex and my company is TechCorp.",
            "alex@techcorp.com"
        )
        
        print(f"\nAI Title: {analysis.title}")
        print(f"AI Suggestions: {analysis.resolution_suggestions}")
        
        # Check if AI followed instructions to be specific
        # We can't strictly assert AI content, but we can look for the ID
        has_id = any("#ORD-998" in s or "ORD-998" in s for s in analysis.resolution_suggestions)
        print(f"AI used specific Order ID: {has_id}")
        
    except Exception as e:
        print(f"Live AI Error (expected if 429): {e}")

if __name__ == "__main__":
    test_smart_fallback()
    asyncio.run(test_live_customization())
