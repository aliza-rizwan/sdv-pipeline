from kuksa_client.grpc import VSSClient, Datapoint
import json
import time

from pathlib import Path

DATA_FILE = Path(__file__).resolve().parents[1] / "simulator" / "vehicle_data.json"

client = VSSClient("127.0.0.1", 55555)
client.connect() 

BATTERY_PATH = "Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"
FAULT_PATH = "Vehicle.OBD.DriveCycleStatus.DTCCount"
fault_path_unavailable = False

while True:

    if not DATA_FILE.exists():
        time.sleep(0.5)
        continue
    try:
        with open(DATA_FILE) as f:
            data = json.load(f)
    except json.JSONDecodeError:
        time.sleep(0.1)
        continue

    updates = {
        "Vehicle.Speed": Datapoint(data["speed"]),
        "Vehicle.Chassis.SteeringWheel.Angle": Datapoint(data["steering_angle"]),
        BATTERY_PATH: Datapoint(data["battery_level"]),
    }

    if not fault_path_unavailable:
        updates[FAULT_PATH] = Datapoint(data["fault_flag"])

    try:
        client.set_current_values(updates)
    except Exception as exc:
        if FAULT_PATH in str(exc):
            fault_path_unavailable = True
            print(f"Warning: fault path unavailable in Kuksa ({FAULT_PATH}). Continuing without fault_flag sync.")
            client.set_current_values({
                "Vehicle.Speed": Datapoint(data["speed"]),
                "Vehicle.Chassis.SteeringWheel.Angle": Datapoint(data["steering_angle"]),
                BATTERY_PATH: Datapoint(data["battery_level"]),
            })
        else:
            raise

    print("Sent to Kuksa:", data)

    time.sleep(1)