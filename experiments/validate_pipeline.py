import argparse
import time

import requests

DEFAULT_URL = "http://127.0.0.1:5001/diagnostics/state"
REQUIRED_KEYS = {
    "speed",
    "steering_angle",
    "battery_level",
    "fault_flag",
    "vehicle_id",
    "sequence",
    "generated_at_ms",
}


def parse_args():
    parser = argparse.ArgumentParser(description="Functional validation for iteration 2 pipeline.")
    parser.add_argument("--url", default=DEFAULT_URL, help="Diagnostics state endpoint URL")
    parser.add_argument("--samples", type=int, default=10, help="Number of samples to validate")
    parser.add_argument("--interval", type=float, default=1.0, help="Sampling interval in seconds")
    return parser.parse_args()


def main():
    args = parse_args()
    previous_sequence = None

    for index in range(1, args.samples + 1):
        response = requests.get(args.url, timeout=5)
        response.raise_for_status()
        data = response.json()

        missing = REQUIRED_KEYS.difference(data.keys())
        if missing:
            raise ValueError(f"Missing keys in sample {index}: {sorted(missing)}")

        sequence = data["sequence"]
        if not isinstance(sequence, int) or sequence <= 0:
            raise ValueError(f"Invalid sequence in sample {index}: {sequence}")

        if previous_sequence is not None and sequence < previous_sequence:
            raise ValueError(
                f"Sequence regressed at sample {index}: previous={previous_sequence}, current={sequence}"
            )

        previous_sequence = sequence
        print(f"Sample {index}/{args.samples}: OK sequence={sequence} fault_flag={data['fault_flag']}")
        time.sleep(args.interval)

    print("Functional validation passed")


if __name__ == "__main__":
    main()
