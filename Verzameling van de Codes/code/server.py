from flask import Flask, render_template, Response
import cv2 as cv

app = Flask(__name__)

def gen_frames(buffer):
    while True:
        count, frame = buffer.get()
        _, encoded = cv.imencode('.jpg', frame)
        bytes_frame = encoded.tobytes()
        yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + bytes_frame + b'\r\n')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

app.run(host='0.0.0.0', debug=True)
