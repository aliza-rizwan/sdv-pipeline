import random
import json
import time
import os


SIMULATOR_FILE = "simulator/vehicle_data.json"


def get_publish_interval_sec():
    raw_value = os.getenv("SIM_INTERVAL_SEC", "1.0")
    try:
        value = float(raw_value)
        if value <= 0:
            raise ValueError
        return value
    except ValueError:
        print(f"Invalid SIM_INTERVAL_SEC='{raw_value}', falling back to 1.0s")
        return 1.0

def generate_vehicle_data(sequence):

    now_ms = int(time.time() * 1000)

    data = {
        "speed": random.randint(0,120),
        "steering_angle": random.randint(-30,30),
        "battery_level": random.randint(30,100),

        # functional modification: simulated fault
        "fault_flag": random.choice([0,1]),
        "vehicle_id": "car01",
        "sequence": sequence,
        "generated_at_ms": now_ms
    }

    return data


if __name__ == "__main__":

    publish_interval_sec = get_publish_interval_sec()
    sequence = 1

    while True:

        vehicle_data = generate_vehicle_data(sequence)

        with open(SIMULATOR_FILE,"w") as f:
            json.dump(vehicle_data,f)

        print("Generated:",vehicle_data)

        sequence += 1

        time.sleep(publish_interval_sec)