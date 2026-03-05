import requests, traceback
from flask import Flask, request
from ai_engine import AIEngine
from audio_player import AudioPlayer

app = Flask(__name__)
ai = AIEngine(api_key="YOUR_GEMINI_API_KEY")
audio = AudioPlayer()
CAMERA_IP = "http://192.168.X.X" # Replace with ESP32 Camera IP

@app.route('/trigger_capture', methods=['GET'])
def trigger_capture():
    try:
        print("📸 Fetching image from Camera...")
        response = requests.get(f"{CAMERA_IP}/capture", timeout=5)
        response.raise_for_status()
        
        print("🧠 Analyzing with Gemini...")
        data = ai.analyze_math_image(response.content)
        
        print("🎧 Generating Audio...")
        new_tracks = 0
        for item in data.get('items', []):
            audio.generate_and_add_tts(item['audio_script'], item['id'])
            new_tracks += 1
            
        return f"Erfolg: {new_tracks} neue Aufgaben. Playlist-Länge: {len(audio.playlist)}"
    except Exception as e:
        traceback.print_exc()
        return f"Fehler: {str(e)}", 500

@app.route('/control', methods=['GET'])
def control():
    cmd = request.args.get('cmd')
    return audio.execute_command(cmd)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)