from flask import Flask, render_template, jsonify
import json, os, subprocess, atexit, psutil

app = Flask(__name__)
STATUS_FILE, LOG_FILE = "status.json", "backend.log"

with open(LOG_FILE, "w") as f: f.write("[*] EDR Telemetry Server Initialized.\n")
with open(STATUS_FILE, "w") as f: json.dump({"status": "SAFE", "last_file": "None", "entropy": "0.00", "message": "System idle. Monitoring I/O..."}, f)

watcher_process = subprocess.Popen(["python", "watcher.py"])

@app.route('/')
def index(): return render_template('index.html')

@app.route('/api/status')
def status():
    try:
        with open(STATUS_FILE, "r") as f: return jsonify(json.load(f))
    except: return jsonify({"status": "SAFE", "last_file": "None", "entropy": "0.00", "message": "Updating..."})

@app.route('/api/logs')
def get_logs():
    try:
        with open(LOG_FILE, "r") as f: return jsonify({"logs": "".join(f.readlines()[-10:])})
    except: return jsonify({"logs": ""})

@app.route('/api/attack/<mode>', methods=['POST'])
def trigger_attack(mode):
    global watcher_process
    watcher_process.kill()
    with open(LOG_FILE, "a") as f: f.write(f"\n[{mode.upper()} SIMULATION INITIATED]\n")
    with open(STATUS_FILE, "w") as f: json.dump({"status": "SAFE", "last_file": "Generating...", "entropy": "0.00", "message": "Injecting payload..."}, f)
    
    watcher_process = subprocess.Popen(["python", "watcher.py"])
    subprocess.Popen(["python", "fake_ransomware.py", mode])
    return jsonify({"success": True})

@app.route('/api/stop', methods=['POST'])
def stop():
    for proc in psutil.process_iter(['cmdline']):
        try:
            if proc.info['cmdline'] and 'fake_ransomware.py' in ' '.join(proc.info['cmdline']): proc.kill()
        except: pass
    with open(STATUS_FILE, "w") as f: json.dump({"status": "SAFE", "last_file": "None", "entropy": "0.00", "message": "Memory purged. System Secure."}, f)
    with open(LOG_FILE, "a") as f: f.write("[*] SYSTEM RESET. RAM Purged.\n")
    return jsonify({"success": True})

if __name__ == '__main__':
    atexit.register(lambda: watcher_process.kill())
    app.run(debug=True, port=5000, use_reloader=False)