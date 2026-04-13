from flask import Flask, request, jsonify

app = Flask(__name__)

data_sensor = {"ph": 0, "ppm": 0}

@app.route('/data', methods=['POST'])
def receive_data():
    global data_sensor
    data_sensor = request.json
    return jsonify({"status": "ok"})

@app.route('/data', methods=['GET'])
def send_data():
    return jsonify(data_sensor)

if __name__ == "__main__":
    app.run()