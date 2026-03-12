import json
from pathlib import Path

import requests

THING_ID = "vehicle:car01"
POLICY_ID = "vehicle:car01-policy"
THING_URL = f"http://localhost:8080/api/2/things/{THING_ID}"
POLICY_URL = f"http://localhost:8080/api/2/policies/{POLICY_ID}"
AUTH = ("ditto", "ditto")

CONFIG_DIR = Path(__file__).resolve().parents[1] / "config"
THING_FILE = CONFIG_DIR / "VSS_Ditto.json"
POLICY_FILE = CONFIG_DIR / "policy.json"


def load_json(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def main():
    headers = {"Content-Type": "application/json"}

    try:
        policy_payload = load_json(POLICY_FILE)
        policy_response = requests.put(POLICY_URL, json=policy_payload, headers=headers, auth=AUTH, timeout=5)
        print(f"Policy response: {policy_response.status_code} {policy_response.text}")

        thing_payload = load_json(THING_FILE)
        thing_response = requests.put(THING_URL, json=thing_payload, headers=headers, auth=AUTH, timeout=5)
        print(f"Thing response: {thing_response.status_code} {thing_response.text}")
    except requests.RequestException as exc:
        print(f"Ditto connection error: {exc}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()