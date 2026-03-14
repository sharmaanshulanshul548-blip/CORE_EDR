import os, time, shutil, sys, urllib.request

TARGET_DIR = "hackathon_test_folder"
CANARY_FILE = "!000_AAA_Financial_Passwords.txt"

def setup_files(include_canary):
    if os.path.exists(TARGET_DIR): shutil.rmtree(TARGET_DIR)
    os.makedirs(TARGET_DIR)
    
    if include_canary:
        with open(os.path.join(TARGET_DIR, CANARY_FILE), "w") as f:
            f.write("SECRET_CANARY_DATA " * 100)

    for i in range(1, 6):
        with open(os.path.join(TARGET_DIR, f"financial_record_{i}.txt"), "w") as f:
            f.write("Sensitive Financial Data - Confidential " * 50)

def attack_ransomware():
    files = sorted(os.listdir(TARGET_DIR))
    for filename in files:
        path = os.path.join(TARGET_DIR, filename)
        if path.endswith(".locked"): continue
        
        # 1. Scramble and FORCE save to disk immediately!
        with open(path, "wb") as f: 
            f.write(os.urandom(2048))
            f.flush()
            os.fsync(f.fileno()) 
            
        time.sleep(0.5) # Give EDR a split-second to scan before renaming
        
        # 2. Rename to .locked
        os.rename(path, path + ".locked")
        print(f"[-] Locked: {filename}")
        time.sleep(0.5)

def attack_spyware():
    print("[-] Reading sensitive files...")
    time.sleep(1)
    for i in range(15):
        try:
            print(f"[-] Exfiltrating data packet {i+1}/15...")
            urllib.request.urlopen("http://www.google.com", timeout=2)
            time.sleep(0.4)
        except:
            print("[X] Connection severed by EDR.")
            break

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "behavioral"
    
    if mode == "spyware":
        time.sleep(2)
        attack_spyware()
    else:
        setup_files(include_canary=(mode == "canary"))
        time.sleep(2)
        attack_ransomware()