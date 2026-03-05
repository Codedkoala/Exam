import json
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        self.model = 'gemini-3.1-pro-preview'

    def analyze_math_image(self, img_bytes):
        system_prompt = """Du bist ein präziser Mathe-Tutor für Klausuren.
        AUFGABE: Analysiere das Bild, finde die mathematischen Aufgaben und löse sie.
        1. NUR DER LÖSUNGSWEG: Keine Einleitung. Nenne kurz die Aufgabe und gehe sofort in die Rechenschritte über.
        2. WENIG TEXT: Nutze nur Mindestworte (z.B. 'Wir klammern x aus').
        3. AUDIO-FORMAT: Schreibe mathematische Zeichen aus (z.B. 'x Quadrat').
        Antworte NUR im exakten JSON-Format: {"items": [{"id": "aufgabe_1", "audio_script": "..."}]}"""

        response = self.client.models.generate_content(
            model=self.model, 
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                system_prompt
            ],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        return json.loads(response.text)
