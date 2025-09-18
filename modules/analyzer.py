import os
import google.generativeai as genai
import json
from dotenv import load_dotenv

load_dotenv()

# Add multiple API keys
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
]
current_key_index = 0

def get_next_api_key():
    global current_key_index
    start_index = current_key_index
    
    while True:
        api_key = API_KEYS[current_key_index]
        if api_key:  # Check if key is not None or empty
            return api_key
            
        current_key_index = (current_key_index + 1) % len(API_KEYS)
        if current_key_index == start_index:
            return None  # All keys are invalid

def analyze_policy_text(text, target_language="English"):
    """
    Uses the Gemini LLM to summarize, analyze risk, and translate policy text.
    """
    # Truncate text if too long to avoid quota issues
    max_length = 12000
    if len(text) > max_length:
        text = text[:max_length] + "..."

    prompt = f"""
    You are an expert legal analyst specializing in online privacy and terms of service.
    Your task is to analyze the following policy text and provide a structured JSON output.
    The analysis should be clear, concise, and easy for a non-expert to understand.

    Policy Text:
    ---
    {text}
    ---

    Perform the following actions:
    1.  **Summarize**: Provide a brief, easy-to-understand summary of the key points.
    2.  **Categorize Risk**: Classify the policy into one of three risk levels: 'Safe', 'Medium Risk', or 'High Risk'.
        - 'Safe': The policy is clear, standard, and respects user privacy with no concerning clauses.
        - 'Medium Risk': The policy contains some ambiguous language, collects more data than necessary, or shares data with third parties in a non-transparent way.
        - 'High Risk': The policy contains clauses that are hostile to user privacy, claims broad rights over user content, or has unclear terms about data security and usage.
    3.  **Identify Key Risks**: List the top 3-5 most important potential risks or points of concern for the user. If there are no significant risks, state that.
    4.  **Translate**: Translate the summary and key risks into **{target_language}**.

    Provide the output in the following JSON format ONLY:
    {{
      "summary": "...",
      "risk_category": "...",
      "key_risks": [
        "...",
        "..."
      ],
      "translated_summary": "...",
      "translated_key_risks": [
        "...",
        "..."
      ]
    }}
    """

    try:
        # Configure with next available API key
        api_key = get_next_api_key()
        if not api_key:
            return {"error": "No valid API key found"}
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 0.8,
                "top_k": 40,
                "max_output_tokens": 2048,
            },
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
                }
            ]
        )
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_response)
    except Exception as e:
        if "429" in str(e):  # Rate limit error
            return {"error": "API rate limit reached. Please try again in a few minutes or contact support to upgrade your API quota."}
        if "All API keys have reached their quota" in str(e):
            return {"error": "All API keys have reached their quota. Please try again later."}
        return {"error": f"Analysis failed: {str(e)}"}
