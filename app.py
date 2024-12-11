# app.py
from flask import Flask, render_template_string
import subprocess
import time
from threading import Thread, Lock

app = Flask(__name__)
data_lock = Lock()
latest_data = {'temp': 0, 'hum': 0}

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>SHT40 Monitor</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f0f2f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1a73e8;
            text-align: center;
            margin-bottom: 30px;
        }
        .sensor-data {
            display: flex;
            justify-content: space-around;
            margin: 20px 0;
        }
        .sensor-box {
            text-align: center;
            padding: 20px;
            border-radius: 8px;
            width: 45%;
        }
        .temp-box {
            background: linear-gradient(135deg, #ff6b6b, #ffa1a1);
            color: white;
        }
        .hum-box {
            background: linear-gradient(135deg, #4facfe, #00f2fe);
            color: white;
        }
        .value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .label {
            font-size: 18px;
            opacity: 0.9;
        }
        .update-time {
            text-align: center;
            color: #666;
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>SHT40 Sensor Monitor</h1>
        <div class="sensor-data">
            <div class="sensor-box temp-box">
                <div class="label">Temperature</div>
                <div class="value"><span id="temp">--</span>°C</div>
            </div>
            <div class="sensor-box hum-box">
                <div class="label">Humidity</div>
                <div class="value"><span id="hum">--</span>%</div>
            </div>
        </div>
        <div class="update-time">Last update: <span id="update-time">--</span></div>
    </div>

    <script>
        function updateData() {
            fetch('/data')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('temp').textContent = data.temp.toFixed(1);
                    document.getElementById('hum').textContent = data.hum.toFixed(1);
                    document.getElementById('update-time').textContent = new Date().toLocaleTimeString();
                });
        }
        setInterval(updateData, 2000);
        updateData();
    </script>
</body>
</html>
'''

def read_sensor():
    while True:
        try:
            result = subprocess.run(['./sht40'], capture_output=True, text=True)
            if result.returncode == 0:
                with data_lock:
                    # Parse output from C program
                    lines = result.stdout.split('\n')
                    if len(lines) >= 2:
                        latest_data['temp'] = float(lines[0])
                        latest_data['hum'] = float(lines[1])
        except Exception as e:
            print(f"Error reading sensor: {e}")
        time.sleep(2)

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/data')
def get_data():
    with data_lock:
        return latest_data

if __name__ == '__main__':
    sensor_thread = Thread(target=read_sensor, daemon=True)
    sensor_thread.start()
    app.run(host='0.0.0.0', port=5000)