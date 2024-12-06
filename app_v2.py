from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime, timedelta
import logging
from pytz import timezone

app = Flask(__name__)
# Define timezone
target_timezone = timezone("America/Toronto")
app.config['DEFAULT_TIMEZONE'] = target_timezone
CORS(app)
DATABASE = 'greenhouse.db'
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
heartbeat_data = {}  # Dictionary to store heartbeat data

def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn

def create_tables():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            time DATETIME NOT NULL,
            event TEXT NOT NULL,
            data TEXT NOT NULL
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS heartbeat (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

create_tables()

@app.route('/registerLog', methods=['POST'])
def register_log():
    logs = request.json.get('logs', [])
    conn = get_db()
    cursor = conn.cursor()
    current_time = datetime.now(target_timezone).strftime('%Y-%m-%d %H:%M:%S')  # Get current server time formatted as a string
    for log in logs:
        cursor.execute('INSERT INTO logs (time, event, data) VALUES (?, ?, ?)', 
                       (current_time, log['event'], log['data']))  # Use current_time instead of log['time']
    conn.commit()
    conn.close()
    return jsonify({"status": "success"}), 201

@app.route('/fetchLastLog', methods=['GET'])
def fet_last_log():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY id DESC LIMIT 1')
    rows = cursor.fetchall()
    conn.close()
    formatted_log = {
        "id": row[0],
        "time": row[1],
        "event": row[2],
        "data": row[3]
    }
    return jsonify(formatted_log), 200

@app.route('/fetchLogs', methods=['GET'])
def fetch_logs():
    last_24_hours = datetime.now(target_timezone) - timedelta(days=1)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs WHERE time > ? ORDER BY id DESC', (last_24_hours,))
    rows = cursor.fetchall()
    conn.close()
    formatted_logs = []
    for row in rows:
      formatted_logs.append({
        "id": row[0],
        "time": row[1],
        "event": row[2],
        "data": row[3]
      })
    return jsonify(formatted_logs), 200

@app.route('/fetchAllLogs', methods=['GET'])
def fetch_all_logs():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM logs ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    formatted_logs = []
    for row in rows:
      formatted_logs.append({
        "id": row[0],
        "time": row[1],
        "event": row[2],
        "data": row[3]
      })
    return jsonify(formatted_logs), 200

@app.route('/heartBeat', methods=['GET'])
def heart_beat():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM heartbeat')
    rows = cursor.fetchall()
    # Clear the heartbeat table
    cursor.execute('DELETE FROM heartbeat')
    conn.commit()
    conn.close()
    # Convert list of tuples into a dictionary and return
    heartbeat_data = {key: value for key, value in rows}
    return jsonify(heartbeat_data), 200

@app.route('/nextHeartBeat', methods=['GET'])
def next_heart_beat():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT key, value FROM heartbeat')
    rows = cursor.fetchall()
    conn.close()
    # Convert list of tuples into a dictionary
    heartbeat_data = {key: value for key, value in rows}
    return jsonify(heartbeat_data), 200

@app.route('/setMaxTemp', methods=['POST'])
def set_max_temp():
    new_max_temp = request.json.get('maxTemp')
    update_heartbeat("maxTemp", new_max_temp)
    return jsonify({"status": "success"}), 201

@app.route('/setMinTemp', methods=['POST'])
def set_min_temp():
    new_min_temp = request.json.get('minTemp')
    update_heartbeat("minTemp", new_min_temp)
    return jsonify({"status": "success"}), 201

@app.route('/setMorningTime', methods=['POST'])
def set_morning_time():
    morning_time = request.json.get('morningTime')
    update_heartbeat("morningTime", morning_time)
    return jsonify({"status": "success"}), 201

@app.route('/setNightTime', methods=['POST'])
def set_night_time():
    night_time = request.json.get('nightTime')
    update_heartbeat("nightTime", night_time)
    return jsonify({"status": "success"}), 201

@app.route('/setNightTempDifference', methods=['POST'])
def set_night_temp_difference():
    night_temp_difference = request.json.get('nightTempDifference')
    update_heartbeat("nightTempDifference", night_temp_difference)
    return jsonify({"status": "success"}), 201

@app.route('/setHealthCheck', methods=['POST'])
def set_health_check():
    healthCheck = request.json.get('healthCheck')
    update_heartbeat("healthCheck", 1)
    return jsonify({"status": "success"}), 201

@app.route('/resetDefaults', methods=['POST'])
def reset_defaults():
    update_heartbeat("resetDefaults", 1)
    return jsonify({"status": "success"}), 201

@app.route('/setHeartbeatPeriod', methods=['POST'])
def set_heartbeat_period():
    heartbeatPeriod = request.json.get('heartbeatPeriod')
    update_heartbeat("heartbeatPeriod", heartbeatPeriod)
    return jsonify({"status": "success"}), 201

def update_heartbeat(key, value):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('REPLACE INTO heartbeat (key, value) VALUES (?, ?)', (key, value))
    conn.commit()
    conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)