from flask import Flask, render_template, Response, jsonify, request
from final import run_camera, get_latest_text, toggle_speech

app = Flask(__name__)

camera_running = False
camera_generator = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    global camera_running, camera_generator
    if not camera_running:
        camera_generator = run_camera()
        camera_running = True
    return Response(camera_generator, mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_text')
def get_text():
    return jsonify({"text": get_latest_text()})

@app.route('/toggle_speech', methods=['POST'])
def toggle_speech_route():
    data = request.get_json()
    toggle_speech(data['enable'])
    return jsonify({"status": "ok"})

@app.route('/stop_camera')
def stop_camera():
    global camera_running, camera_generator
    camera_generator = None
    camera_running = False
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(debug=True)
