#  CORE_EDR: Next-Gen Behavioral Endpoint Defense

Traditional antivirus relies on outdated signature blacklists. **CORE_EDR** is a real-time, behavioral analysis engine designed to detect and neutralize Zero-Day ransomware and silent data exfiltration (spyware) in milliseconds.

##  Core Features
* **Process Suspension:** The moment anomalous file I/O is detected, the suspected process is frozen in memory (`psutil.suspend()`), preventing further damage while the engine calculates the threat.
* **Shannon Entropy Engine:** Bypasses blacklists by calculating the mathematical randomness (chaos) of modified files. If a file is encrypted by ransomware, the entropy spikes above `7.5`, and the threat is instantly terminated.
* **Network Socket Telemetry:** A background sentinel thread monitors the OS network stack. It correlates suspicious processes with unauthorized `ESTABLISHED` TCP outbound connections, instantly blocking data exfiltration and mapping the hacker's IP and Port.
* **O(1) Canary Tripwires:** Strategic hidden files (`!000_AAA...`) placed at the top of directories act as honeypots, instantly killing ransomware on the very first file access to save CPU overhead.

##  Tech Stack
* **Backend Engine:** Python (`watchdog`, `psutil`, `math`)
* **Telemetry Server:** Flask 
* **Frontend UI:** HTML/CSS/JS (Cyberpunk Command Center Aesthetic)

##  How to Run Locally
1. Clone the repository or download the ZIP.
2. Install the required dependencies:
   `pip install flask psutil watchdog`
3. **Important:** Open your Command Prompt or Terminal as an **Administrator** (required for the network socket monitoring to work).
4. Run the telemetry server:
   `python app.py`
5. Open your browser and navigate to `http://127.0.0.1:5000`.

*Disclaimer: The `fake_ransomware.py` script provided is a safe, benign simulation tool built strictly for testing this EDR in a hackathon environment. It generates dummy files and does not harm real system data.*
