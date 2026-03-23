from flask import Flask, jsonify
import requests
import time

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
        "vehicle_id": features.get("vehicle_id", {}).get("properties", {}).get("value"),
        "sequence": features.get("sequence", {}).get("properties", {}).get("value"),
        "generated_at_ms": features.get("generated_at_ms", {}).get("properties", {}).get("value"),
        "middleware_received_at_ms": features.get("middleware_received_at_ms", {}).get("properties", {}).get("value"),
    }

@app.route("/diagnostics/state", methods=["GET"])
def get_vehicle_state():
    try:
        telemetry = fetch_telemetry()
    except (requests.RequestException, ValueError) as exc:
        return jsonify({"error": str(exc)}), 500

    diagnostics = {
        "speed": telemetry.get("speed"),
        "steering_angle": telemetry.get("steering_angle"),
        "battery_level": telemetry.get("battery_level"),
        "fault_flag": telemetry.get("fault_flag"),
        "vehicle_id": telemetry.get("vehicle_id"),
        "sequence": telemetry.get("sequence"),
        "generated_at_ms": telemetry.get("generated_at_ms"),
        "middleware_received_at_ms": telemetry.get("middleware_received_at_ms")
    }

    generated_at_ms = telemetry.get("generated_at_ms")
    if isinstance(generated_at_ms, (int, float)) and generated_at_ms > 0:
        diagnostics["end_to_end_latency_ms"] = int(time.time() * 1000) - int(generated_at_ms)

    return jsonify(diagnostics)


@app.route("/diagnostics/faults", methods=["GET"])
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