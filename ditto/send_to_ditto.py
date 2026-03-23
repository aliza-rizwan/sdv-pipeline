import json
import time
from pathlib import Path

import requests

thingsURL = "http://localhost:8080/api/2/things/"
policiesURL = "http://localhost:8080/api/2/policies/"
auth = ("ditto", "ditto")

THING_ID = "vehicle:car01"
POLICY_ID = "vehicle:car01-policy"
ZENOH_DATA_FILE = Path(__file__).resolve().parents[1] / "middleware" / "zenoh_data.json"
POLICY_FILE = Path(__file__).resolve().parents[1] / "config" / "policy.json"
THING_FILE = Path(__file__).resolve().parents[1] / "config" / "VSS_Ditto.json"
REQUIRED_KEYS = {"speed", "steering_angle", "battery_level", "fault_flag"}


def get_thing(thingID):
    url = thingsURL + thingID
    response = requests.get(url, auth=auth, timeout=5)
    if response.status_code == 404:
        return None
    return response.json()


def put_thing(thingID, ThingData):
    url = thingsURL + thingID
    headers = {"Content-Type": "Application/json"}
    response = requests.put(url, json=ThingData, headers=headers, auth=auth, timeout=5)
    return response


def patch_thing(thingID, ThingData):
    url = thingsURL + thingID
    headers = {"Content-Type": "Application/merge-patch+json"}
    response = requests.patch(url, json=ThingData, headers=headers, auth=auth, timeout=5)
    return response


def delete_thing(thingID):
    url = thingsURL + thingID
    response = requests.delete(url, auth=auth, timeout=5)
    return response


def put_policy(policyID, PolicyData):
    url = policiesURL + policyID
    headers = {"Content-Type": "Application/json"}
    response = requests.put(url, json=PolicyData, headers=headers, auth=auth, timeout=5)
    return response


def delete_policy(policyID):
    url = policiesURL + policyID
    response = requests.delete(url, auth=auth, timeout=5)
    return response


def get_feature_value(thingID, feature):
    url = thingsURL + thingID + "/features/" + feature + "/properties/value"
    response = requests.get(url, auth=auth, timeout=5)
    if response.status_code == 200:
        return float(response.json())
    return response


def put_feature_value(thingID, feature, value):
    url = thingsURL + thingID + "/features/" + feature + "/properties"
    headers = {"Content-Type": "Application/json"}
    data = {"value": value}
    response = requests.put(url, json=data, headers=headers, auth=auth, timeout=5)
    return response


def bootstrap_ditto():
    if POLICY_FILE.exists():
        with open(POLICY_FILE, "r", encoding="utf-8") as file:
            policy = json.load(file)
        response = put_policy(POLICY_ID, policy)
        print(f"Policy upsert status: {response.status_code}")

    if get_thing(THING_ID) is None:
        with open(THING_FILE, "r", encoding="utf-8") as file:
            thing = json.load(file)
        response = put_thing(THING_ID, thing)
        print(f"Thing create status: {response.status_code}")


def read_zenoh_payload():
    with open(ZENOH_DATA_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    if not REQUIRED_KEYS.issubset(data.keys()):
        missing = REQUIRED_KEYS.difference(data.keys())
        raise ValueError(f"incomplete telemetry, missing {sorted(missing)}")

    return data


def main():
    bootstrap_ditto()

    while True:
        try:
            if not ZENOH_DATA_FILE.exists():
                print(f"Waiting for Zenoh data file: {ZENOH_DATA_FILE}")
                time.sleep(1)
                continue

            payload = read_zenoh_payload()
            patch = {
                "features": {
                    "speed": {
                        "properties": {"value": payload["speed"]}
                    },
                    "steering_angle": {
                        "properties": {"value": payload["steering_angle"]}
                    },
                    "battery_level": {
                        "properties": {"value": payload["battery_level"]}
                    },
                    "fault_flag": {
                        "properties": {"value": payload["fault_flag"]}
                    },
                    "vehicle_id": {
                        "properties": {"value": payload.get("vehicle_id", "car01")}
                    },
                    "sequence": {
                        "properties": {"value": payload.get("sequence", 0)}
                    },
                    "generated_at_ms": {
                        "properties": {"value": payload.get("generated_at_ms", 0)}
                    },
                    "middleware_received_at_ms": {
                        "properties": {"value": payload.get("middleware_received_at_ms", 0)}
                    }
                }
            }

            response = patch_thing(THING_ID, patch)
            if response.status_code >= 400:
                print(f"Ditto update failed ({response.status_code}): {response.text}")
            else:
                print("Updated Ditto:", payload)

        except requests.RequestException as exc:
            print(f"Ditto connection error: {exc}")
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Telemetry read error: {exc}")

        time.sleep(1)


if __name__ == "__main__":
    main()