import zenoh
import time
import json
import os
from pathlib import Path
from kuksa_client.grpc import VSSClient

# connect to kuksa
client = VSSClient("127.0.0.1", 55555)
client.connect()

signals = [
    "Vehicle.Speed",
    "Vehicle.Chassis.SteeringWheel.Angle",
    "Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"
]
FAULT_PATH = "Vehicle.OBD.DTCCount"
SIMULATOR_FILE = Path(__file__).resolve().parents[1] / "simulator" / "vehicle_data.json"
DEFAULT_METADATA = {
    "vehicle_id": "car01",
    "sequence": 0,
    "generated_at_ms": 0
}
PUBLISH_INTERVAL_SEC = float(os.getenv("PUBLISH_INTERVAL_SEC", "1.0"))

# connect to zenoh
session = zenoh.open(zenoh.Config())

key = "vehicle/data"


def unwrap_value(value):
    return value.value if hasattr(value, "value") else value


def read_simulator_metadata():
    if not SIMULATOR_FILE.exists():
        return DEFAULT_METADATA.copy()

    try:
        with open(SIMULATOR_FILE, "r", encoding="utf-8") as file:
            simulator_data = json.load(file)

        return {
            "vehicle_id": str(simulator_data.get("vehicle_id", "car01")),
            "sequence": int(simulator_data.get("sequence", 0)),
            "generated_at_ms": int(simulator_data.get("generated_at_ms", 0))
        }
    except (json.JSONDecodeError, OSError, TypeError):
        return DEFAULT_METADATA.copy()

while True:

    values = client.get_current_values(signals)

    fault_flag = 0
    try:
        fault_values = client.get_current_values([FAULT_PATH])
        fault_flag = int(unwrap_value(fault_values[FAULT_PATH]))
    except Exception:
        if SIMULATOR_FILE.exists():
            try:
                with open(SIMULATOR_FILE) as f:
                    simulator_data = json.load(f)
                fault_flag = int(simulator_data.get("fault_flag", 0))
            except (json.JSONDecodeError, OSError):
                fault_flag = 0

    data = {
        "speed": unwrap_value(values["Vehicle.Speed"]),
        "steering_angle": unwrap_value(values["Vehicle.Chassis.SteeringWheel.Angle"]),
        "battery_level": unwrap_value(values["Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"]),
        "fault_flag": fault_flag
    }

    data.update(read_simulator_metadata())

    session.put(key, json.dumps(data))

    print("Published to Zenoh:", data)

    time.sleep(PUBLISH_INTERVAL_SEC)