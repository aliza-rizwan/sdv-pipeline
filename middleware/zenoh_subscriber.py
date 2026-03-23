import zenoh
import time
import json
import os
import random
from pathlib import Path

session = zenoh.open(zenoh.Config())

key = "vehicle/data"
OUTPUT_FILE = Path(__file__).resolve().parent / "zenoh_data.json"
REQUIRED_KEYS = {"speed", "steering_angle", "battery_level", "fault_flag"}
DROP_PROBABILITY = float(os.getenv("ZENOH_DROP_PROB", "0.0"))
DELAY_MS = int(os.getenv("ZENOH_DELAY_MS", "0"))


def now_ms():
    return int(time.time() * 1000)

def listener(sample):
    payload = sample.payload
    message = payload.to_string() if hasattr(payload, "to_string") else str(payload)

    if DROP_PROBABILITY > 0 and random.random() < DROP_PROBABILITY:
        print("Dropped message in middleware fault injector")
        return

    try:
        data = json.loads(message)
        if not REQUIRED_KEYS.issubset(data.keys()):
            missing = REQUIRED_KEYS.difference(data.keys())
            print(f"Skipping incomplete payload, missing keys: {sorted(missing)}")
            return

        if DELAY_MS > 0:
            time.sleep(DELAY_MS / 1000.0)

        data["middleware_received_at_ms"] = now_ms()

        with open(OUTPUT_FILE, "w") as f:
            json.dump(data, f)
    except json.JSONDecodeError:
        pass
    print("Received from Zenoh:", message)

subscriber = session.declare_subscriber(key, listener)

print("Zenoh subscriber running...")

while True:
    time.sleep(1)