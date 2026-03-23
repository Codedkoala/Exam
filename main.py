import os, requests, traceback
from flask import Flask, request, render_template_string, send_from_directory
from dotenv import load_dotenv 
from ai_engine import AIEngine
from audio_player import AudioPlayer

load_dotenv(os.path.join(os.getcwd(), '.env'))

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

ai = AIEngine(api_key=api_key)
audio = AudioPlayer()

CAMERA_IP = None 
PENDING_IMAGES = [] 
SOLVED_EXERCISE_IDS = set()

# 📁 IMAGE STORAGE
IMAGE_FOLDER = "images"
os.makedirs(IMAGE_FOLDER, exist_ok=True)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>AI Multi-Scan Tutor</title>
</head>
<body>
    <h2>Camera Dashboard</h2>
    <button onclick="fetch('/trigger_capture')">📸 Capture</button>
    <button onclick="fetch('/control?cmd=next')">➕ Solve</button>
    <br><br>
    <a href="/gallery">📂 View Images</a>
</body>
</html>
"""

@app.route('/register', methods=['GET'])
def register_device():
    global CAMERA_IP
    role = request.args.get('role')
    # Holt sich den Port aus der URL, Standard ist 80 falls keiner gesendet wird
    port = request.args.get('port', '80') 
    device_ip = request.remote_addr 
    
    if role == 'camera':
        CAMERA_IP = f"http://{device_ip}:{port}"
        print(f"📸 Camera registered at {CAMERA_IP}")
        return "Camera Registered", 200
        
    return "OK", 200

@app.route('/')
def dashboard():
    return render_template_string(HTML_PAGE)

# 📸 CAPTURE + SAVE FILES
@app.route('/trigger_capture', methods=['GET'])
def trigger_capture():
    global CAMERA_IP, PENDING_IMAGES

    if not CAMERA_IP:
        return "No camera", 400
        
    try:
        response = requests.get(f"{CAMERA_IP}/capture", timeout=10)
        response.raise_for_status()

        image_content = response.content

        # 🔢 next number
        count = len(PENDING_IMAGES) + 1
        filename = f"{count}.jpg"
        filepath = os.path.join(IMAGE_FOLDER, filename)

        # 💾 save file
        with open(filepath, "wb") as f:
            f.write(image_content)

        # 🧠 keep in RAM
        PENDING_IMAGES.append(image_content)

        print(f"✅ Stored Image {count}")

        return f"Saved Image {count}"

    except Exception as e:
        traceback.print_exc()
        return str(e), 500


# 🧠 SOLVE + MEDIA NAVIGATION
@app.route('/control', methods=['GET'])
def control():
    global PENDING_IMAGES, SOLVED_EXERCISE_IDS

    cmd = request.args.get('cmd')

    # FALL 1: Benutzer drückt "Next" UND es gibt ungelöste Bilder im RAM
    if cmd == 'next' and len(PENDING_IMAGES) > 0:
        print("🧠 Starte KI-Auswertung der gesammelten Bilder...")
        images_to_process = PENDING_IMAGES.copy()
        PENDING_IMAGES.clear()

        try:
            data = ai.analyze_images_multi_context(images_to_process)
            exercises = data.get('exercises', [])

            for exercise in exercises:
                ex_id = exercise['id']
                steps = exercise.get('steps', [])

                if ex_id not in SOLVED_EXERCISE_IDS:
                    SOLVED_EXERCISE_IDS.add(ex_id)
                    # Jeden Lösungsschritt als einzelnen Audio-Track zur Playlist hinzufügen
                    for i, step_text in enumerate(steps):
                        filename = f"{ex_id}_schritt_{i+1}"
                        audio.generate_and_add_tts(step_text, filename)

            # 🧹 CLEAR IMAGE FOLDER
            for file in os.listdir(IMAGE_FOLDER):
                try:
                    os.remove(os.path.join(IMAGE_FOLDER, file))
                except:
                    pass
            print("🧹 Bilder-Cache geleert.")

            # Direkt den ersten neuen Track abspielen!
            if len(audio.playlist) > 0:
                audio.execute_command('play')

            return "Solved + Playlist started"

        except Exception as e:
            traceback.print_exc()
            return "Error", 500

    # FALL 2: Navigation durch die Lösungs-Schritte (Next, Prev, Pause)
    else:
        status = audio.execute_command(cmd)
        return status


# 📂 VIEW IMAGES
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


@app.route('/gallery')
def gallery():
    files = sorted(
        os.listdir(IMAGE_FOLDER),
        key=lambda x: int(x.split('.')[0])
    )

    html = ""
    for f in files:
        html += f'<img src="/images/{f}" width="300"><br>'

    return html


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)