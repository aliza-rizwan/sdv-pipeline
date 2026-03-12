import zenoh
import time
import json
from pathlib import Path

session = zenoh.open(zenoh.Config())

key = "vehicle/data"
OUTPUT_FILE = Path(__file__).resolve().parent / "zenoh_data.json"
REQUIRED_KEYS = {"speed", "steering_angle", "battery_level", "fault_flag"}

def listener(sample):
    payload = sample.payload
    message = payload.to_string() if hasattr(payload, "to_string") else str(payload)
    try:
        data = json.loads(message)
        if not REQUIRED_KEYS.issubset(data.keys()):
            missing = REQUIRED_KEYS.difference(data.keys())
            print(f"Skipping incomplete payload, missing keys: {sorted(missing)}")
            return
        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f)
    except json.JSONDecodeError:
        pass
    print("Received from Zenoh:", message)

subscriber = session.declare_subscriber(key, listener)

print("Zenoh subscriber running...")

while True:
    time.sleep(1)