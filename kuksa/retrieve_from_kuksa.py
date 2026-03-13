from kuksa_client.grpc import VSSClient
import json
import time

client = VSSClient("127.0.0.1", 55555)
client.connect() 

BATTERY_PATH = "Vehicle.Powertrain.TractionBattery.StateOfCharge.Displayed"
FAULT_PATH = "Vehicle.OBD.DriveCycleStatus.DTCCount"


def unwrap_value(value):
    return value.value if hasattr(value, "value") else value

signals = [
    "Vehicle.Speed",
    "Vehicle.Chassis.SteeringWheel.Angle",
    BATTERY_PATH,
    FAULT_PATH,
]

while True:

    try:
        values = client.get_current_values(signals)
    except Exception as exc:
        if FAULT_PATH in str(exc):
            values = client.get_current_values(signals[:-1])
            values[FAULT_PATH] = 0
        else:
            raise

    data = {
        "speed": unwrap_value(values["Vehicle.Speed"]),
        "steering_angle": unwrap_value(values["Vehicle.Chassis.SteeringWheel.Angle"]),
        "battery_level": unwrap_value(values[BATTERY_PATH]),
        "fault_flag": int(unwrap_value(values[FAULT_PATH]))
    }

    with open("kuksa_data.json", "w") as f:
        json.dump(data, f)

    print("Retrieved from Kuksa:", data)

    time.sleep(1)