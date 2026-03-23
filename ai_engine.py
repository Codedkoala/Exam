import json
from google import genai
from google.genai import types

class AIEngine:
    def __init__(self, api_key):
        self.client = genai.Client(api_key=api_key)
        # Using Gemini 1.5 Pro for standard multimodality context handling
        self.model = 'gemini-3.1-pro-preview' 

    def extract_text(self, img_bytes):
        # OCR Function kept for reference, not actively used in renewed multi-image flow
        system_prompt = """Du bist ein Texterkennungs-System. 
        Lies NUR den Text, die Zahlen und Tabellen auf dem Bild vor. Keine Erklärungen."""
        
        response = self.client.models.generate_content(
            model=self.model, 
            contents=[
                types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'),
                system_prompt
            ]
        )
        text = response.text.strip()
        return text

    # --- RENEWED: MULTI-IMAGE COLLECTIVE CONTEXT ---
  # --- RENEWED: MULTI-IMAGE COLLECTIVE CONTEXT ---
    def analyze_images_multi_context(self, images_list):
        """
        Receives a list of image bytes (different angles of same paper).
        Gemini analyzes them collectively to solve all unique tasks.
        """
        
        # 1. Build the multi-part content list
        contents = []
        for img_bytes in images_list:
            contents.append(types.Part.from_bytes(data=img_bytes, mime_type='image/jpeg'))

        # 2. Add the RENEWED tutor prompt for step-by-step Physics & BWR focus
        system_prompt = """Du bist ein präziser, prüfungsorientierter Tutor für Physik und BWR/BWL.

AUFGABE:
Dir werden mehrere Bilder DESSELBEN Dokuments aus verschiedenen Blickwinkeln übergeben, um Unschärfen auszugleichen. Analysiere ALLE Bilder kollektiv als einen einzigen Kontext. Identifiziere alle Aufgaben und löse sie.

WICHTIGE REGELN:
- Prüfungsorientiert: Schreibe so wenig wie möglich, aber so viel wie für die volle Punktzahl in einer Prüfung nötig ist (inkl. Rechenweg).
- Deduplizierung: Löse jede sichtbare Aufgabe nur exakt einmal, auch wenn sie auf mehreren Fotos zu sehen ist.

STRUKTUR DER LÖSUNG (SEHR WICHTIG):
Zerlege JEDE Aufgabe in kleine, logische Einzelschritte, die nacheinander als Audio abgespielt werden. 
- Bei BWR (z.B. 5-Schritt-Methode, Finanzierung): 
  Schritt 1 ist immer das Vorbereiten (z.B. 'Zeichne das Schema für die 5-Schritt-Methode auf'). 
  Folgeschritte füllen das Schema logisch Zeile für Zeile aus.
- Bei Physik: 
  Schritt 1: 'Gegeben und Gesucht'. 
  Schritt 2: 'Formel aufstellen und ggf. umstellen'. 
  Schritt 3: 'Werte einsetzen und ausrechnen'.
- Sprache: Alles auf Deutsch. Schreibe mathematische Zeichen aus (z.B. 'x Quadrat', 'geteilt durch'), da der Text vorgelesen wird. Keine Markdown-Formatierungen in den Schritten!

Antworte NUR im exakten JSON-Format: 
{"exercises": [{"id": "aufgabe_1a", "steps": ["Schritt 1: ...", "Schritt 2: ..."]}, {"id": "aufgabe_1b", "steps": ["..."]}]}"""

        contents.append(system_prompt)

        # 3. Request structured JSON response
        response = self.client.models.generate_content(
            model=self.model, 
            contents=contents,
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )
        
        try:
            return json.loads(response.text)
        except json.JSONDecodeError:
            print(f"❌ ERROR parsing AI JSON response: {response.text}")
            return {"exercises": []}