from flask import Flask, jsonify
import requests

app = Flask(__name__)

DITTO_URL = "http://localhost:8080/api/2/things/vehicle:car01"
AUTH = ("ditto", "ditto")


def fetch_telemetry():
    response = requests.get(DITTO_URL, auth=AUTH, timeout=5)

    if response.status_code != 200:
        raise ValueError(f"Unable to retrieve digital twin: {response.status_code}")

    twin = response.json()
    features = twin.get("features", {})

    return {
        "speed": features.get("speed", {}).get("properties", {}).get("value"),
        "steering_angle": features.get("steering_angle", {}).get("properties", {}).get("value"),
        "battery_level": features.get("battery_level", {}).get("properties", {}).get("value"),
        "fault_flag": features.get("fault_flag", {}).get("properties", {}).get("value"),
    }

@app.route("/diagnostics/state")
def get_vehicle_state():
    try:
        telemetry = fetch_telemetry()
    except (requests.RequestException, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500

    diagnostics = {
        "speed": telemetry.get("speed"),
        "steering_angle": telemetry.get("steering_angle"),
        "battery_level": telemetry.get("battery_level"),
        "fault_flag": telemetry.get("fault_flag")
    }

    return jsonify(diagnostics)


@app.route("/diagnostics/faults")
def get_fault_state():
    try:
        telemetry = fetch_telemetry()
    except (requests.RequestException, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500

    return jsonify({
        "fault_flag": telemetry.get("fault_flag"),
        "battery_health": telemetry.get("battery_level")
    })


if __name__ == "__main__":
    app.run(port=5001)