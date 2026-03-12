import random
import json
import time

def generate_vehicle_data():

    data = {
        "speed": random.randint(0,120),
        "steering_angle": random.randint(-30,30),
        "battery_level": random.randint(30,100),

        # functional modification: simulated fault
        "fault_flag": random.choice([0,1])
    }

    return data


if __name__ == "__main__":

    while True:

        vehicle_data = generate_vehicle_data()

        with open("simulator/vehicle_data.json","w") as f:
            json.dump(vehicle_data,f)

        print("Generated:",vehicle_data)

        time.sleep(1)