import os, time, math, psutil, json, threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_DIR = "."
TARGET_DIR_NAME = "hackathon_test_folder"
STATUS_FILE = "status.json"
LOG_FILE = "backend.log"
CANARY_NAME = "!000_AAA_Financial_Passwords.txt"

system_secured = False

def log_msg(msg):
    print(msg)
    with open(LOG_FILE, "a") as f: f.write(msg + "\n")

def update_status(status, last_file, entropy, message):
    global system_secured
    if status == "SAFE": system_secured = False
    if system_secured and status == "SAFE": return
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": status, "last_file": last_file, "entropy": f"{entropy:.2f}", "message": message}, f)

def calculate_entropy(file_path):
    # FALLBACK: If renamed too fast, check for the .locked version!
    if not os.path.exists(file_path) and os.path.exists(file_path + ".locked"):
        file_path = file_path + ".locked"
        
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
            if not data: return 0.0
            ent = 0
            for x in range(256):
                p_x = float(data.count(x)) / len(data)
                if p_x > 0: ent += - p_x * math.log2(p_x)
            return ent
    except: return 0.0

def monitor_network():
    global system_secured
    while True:
        if system_secured: 
            time.sleep(0.5)
            continue
        try:
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED' and conn.pid and conn.raddr:
                    proc = psutil.Process(conn.pid)
                    if 'fake_ransomware.py' in ' '.join(proc.cmdline()):
                        remote_ip = conn.raddr.ip
                        remote_port = conn.raddr.port
                        
                        log_msg(f"[!!!] UNAUTHORIZED NETWORK SOCKET DETECTED [!!!]")
                        log_msg(f"[*] BLOCKED TCP OUTBOUND | IP: {remote_ip} | PORT: {remote_port}")
                        
                        system_secured = True
                        proc.kill()
                        
                        telemetry_data = f"IP: {remote_ip} // PORT: {remote_port}"
                        update_status("DANGER", telemetry_data, 0.0, "DATA EXFILTRATION (SPYWARE) NEUTRALIZED!")
        except: pass
        time.sleep(0.2)

class EDRHandler(FileSystemEventHandler):
    def on_modified(self, event):
        global system_secured
        if system_secured or TARGET_DIR_NAME not in event.src_path: return
        
        filename = os.path.basename(event.src_path)
        
        for proc in psutil.process_iter(['pid', 'cmdline']):
            if proc.info['cmdline'] and 'fake_ransomware.py' in ' '.join(proc.info['cmdline']):
                proc.suspend()
                
                entropy = calculate_entropy(event.src_path)
                is_canary = (filename == CANARY_NAME or filename == CANARY_NAME + ".locked")
                
                log_msg(f"[*] Layer 1 (Tripwire): {is_canary} | Layer 2 (Entropy): {entropy:.2f}")

                # Threat evaluation
                if is_canary or entropy > 7.5:
                    system_secured = True
                    proc.kill()
                    if is_canary:
                        log_msg(f"[!!!] CANARY TRIPWIRE TRIGGERED BY {filename} [!!!]")
                        update_status("DANGER", filename, entropy, "TRIPWIRE ACTIVATED: Zero-Day Neutralized.")
                    else:
                        log_msg(f"[!] HIGH ENTROPY SPIKE DETECTED in {filename}!")
                        update_status("DANGER", filename, entropy, "BEHAVIORAL ALARM: Ransomware Terminated.")
                else:
                    try: proc.resume()
                    except: pass
                    update_status("SAFE", filename, entropy, "System idle. Monitoring I/O...")

if __name__ == "__main__":
    update_status("SAFE", "None", 0.0, "System idle. Monitoring I/O...")
    threading.Thread(target=monitor_network, daemon=True).start()
    observer = Observer()
    observer.schedule(EDRHandler(), path=WATCH_DIR, recursive=True)
    observer.start()
    try:
        while True:
            try:
                with open(STATUS_FILE, "r") as f:
                    if json.load(f)["status"] == "SAFE": system_secured = False
            except: pass
            time.sleep(1)
    except: observer.stop()
    observer.join()