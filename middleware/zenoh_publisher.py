import zenoh
import time
import json
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

# connect to zenoh
session = zenoh.open(zenoh.Config())

key = "vehicle/data"


def unwrap_value(value):
    return value.value if hasattr(value, "value") else value

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
            except (json.JSONDecodeError, OSError, ValueError):
                fault_flag = 0

    data = {
        "speed": unwrap_value(values["Vehicle.Speed"]),
        "steering_angle": unwrap_value(values["Vehicle.Chassis.SteeringWheel.Angle"]),
        "battery_level": unwrap_value(values["Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"]),
        "fault_flag": fault_flag
    }

    session.put(key, json.dumps(data))

    print("Published to Zenoh:", data)

    time.sleep(1)