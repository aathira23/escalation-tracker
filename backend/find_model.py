
import google.generativeai as genai
from app.config import get_settings

def find_working_model():
    settings = get_settings()
    genai.configure(api_key=settings.gemini_api_key)
    
    # Common model names to try
    models_to_try = [
        'gemini-1.5-flash',
        'gemini-1.5-flash-latest',
        'gemini-1.0-pro',
        'gemini-pro',
        'gemini-2.0-flash',
        'gemini-2.0-flash-exp'
    ]
    
    print("Testing models for connectivity and quota...")
    for model_name in models_to_try:
        print(f"\nTrying: {model_name}...", end=" ", flush=True)
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content("test")
            print("SUCCESS!")
            return model_name
        except Exception as e:
            err_str = str(e)
            if "429" in err_str:
                print("EXISTENT (but rate limited/429). This model IS working.")
                return model_name
            elif "404" in err_str:
                print("NOT FOUND (404).")
            else:
                print(f"FAILED: {err_str}")
    
    return None

if __name__ == "__main__":
    winner = find_working_model()
    if winner:
        print(f"\nFinal Recommendation: Use '{winner}'")
    else:
        print("\nNo working models found. Please check your API key permissions at https://aistudio.google.com/")
