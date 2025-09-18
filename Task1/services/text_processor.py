import re
import google.generativeai as genai
from typing import List
from config import settings  # where your API key is stored

class TextProcessor:
    def __init__(self):
        # Configure Gemini with your API key
        genai.configure(api_key=settings.GEMINI_API_KEY)

    def clean_text(self, raw_text: str) -> str:
        """Clean and normalize extracted text"""
        if not raw_text:
            return ""
        cleaned = re.sub(r'\s+', ' ', raw_text.strip())
        return cleaned

    def extract_keywords(self, text: str) -> List[str]:
        """Extract medical keywords using Gemini"""
        if not text:
            return []
        
        prompt = f"""
        You are a medical text analyzer.
        Extract only relevant **medical keywords** (symptoms, diseases, drugs, measurements, procedures)
        from the following text. Return them as a JSON list of strings, without explanations.

        Text: {text}
        """
        
        model = genai.GenerativeModel("gemini-1.5-flash")  # lightweight + fast
        response = model.generate_content(prompt)
        response_text = response.text
        if response_text.startswith("```"):
            response_text = response_text.split("\n", 1)[1].rsplit("```", 1)[0].strip()
        
        try:
            keywords = eval(response_text)
            if isinstance(keywords, list):
                return keywords[:20]  # limit
            return []
        except Exception:
            return []
