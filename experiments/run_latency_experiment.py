import argparse
import csv
import statistics
import time
from pathlib import Path

import requests

DEFAULT_DITTO_URL = "http://localhost:8080/api/2/things/vehicle:car01"
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "results"
AUTH = ("ditto", "ditto")


def parse_args():
	parser = argparse.ArgumentParser(
		description="Measure end-to-end latency from simulator generation timestamp to Ditto twin state."
	)
	parser.add_argument("--label", required=True, help="Experiment label, for example baseline or fault_injection")
	parser.add_argument("--samples", type=int, default=30, help="Number of unique sequence samples to collect")
	parser.add_argument("--poll-interval", type=float, default=0.2, help="Polling interval in seconds")
	parser.add_argument("--ditto-url", default=DEFAULT_DITTO_URL, help="Ditto thing URL")
	parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR), help="Output directory")
	return parser.parse_args()


def read_features(ditto_url):
	response = requests.get(ditto_url, auth=AUTH, timeout=5)
	response.raise_for_status()
	twin = response.json()
	features = twin.get("features", {})
	return {
		"sequence": features.get("sequence", {}).get("properties", {}).get("value"),
		"generated_at_ms": features.get("generated_at_ms", {}).get("properties", {}).get("value"),
		"middleware_received_at_ms": features.get("middleware_received_at_ms", {}).get("properties", {}).get("value"),
		"fault_flag": features.get("fault_flag", {}).get("properties", {}).get("value"),
		"vehicle_id": features.get("vehicle_id", {}).get("properties", {}).get("value"),
	}


def summarize(latencies):
	return {
		"count": len(latencies),
		"min_ms": round(min(latencies), 2),
		"avg_ms": round(statistics.mean(latencies), 2),
		"p95_ms": round(statistics.quantiles(latencies, n=100)[94], 2) if len(latencies) >= 20 else round(max(latencies), 2),
		"max_ms": round(max(latencies), 2),
	}


def write_samples_csv(path, rows):
	with open(path, "w", newline="", encoding="utf-8") as file:
		writer = csv.DictWriter(
			file,
			fieldnames=[
				"sample_index",
				"vehicle_id",
				"sequence",
				"fault_flag",
				"generated_at_ms",
				"middleware_received_at_ms",
				"observed_at_ms",
				"end_to_end_latency_ms",
			],
		)
		writer.writeheader()
		writer.writerows(rows)


def write_summary_markdown(path, label, summary):
	lines = [
		f"# Latency Summary: {label}",
		"",
		"| Metric | Value (ms) |",
		"|---|---:|",
		f"| min_ms | {summary['min_ms']} |",
		f"| avg_ms | {summary['avg_ms']} |",
		f"| p95_ms | {summary['p95_ms']} |",
		f"| max_ms | {summary['max_ms']} |",
		f"| sample_count | {summary['count']} |",
		"",
		"Mermaid chart:",
		"",
		"```mermaid",
		"xychart-beta",
		"    title End-to-End Latency Summary",
		"    x-axis [min, avg, p95, max]",
		f"    bar [{summary['min_ms']}, {summary['avg_ms']}, {summary['p95_ms']}, {summary['max_ms']}]",
		"```",
		"",
	]
	with open(path, "w", encoding="utf-8") as file:
		file.write("\n".join(lines))


def main():
	args = parse_args()
	output_dir = Path(args.output_dir)
	output_dir.mkdir(parents=True, exist_ok=True)

	seen_sequences = set()
	rows = []
	latencies = []

	print(f"Collecting {args.samples} samples for label '{args.label}'...")

	while len(rows) < args.samples:
		try:
			data = read_features(args.ditto_url)
		except requests.RequestException as exc:
			print(f"Ditto read error: {exc}")
			time.sleep(args.poll_interval)
			continue

		sequence = data.get("sequence")
		generated_at_ms = data.get("generated_at_ms")

		if not isinstance(sequence, int) or sequence <= 0:
			time.sleep(args.poll_interval)
			continue

		if not isinstance(generated_at_ms, (int, float)) or generated_at_ms <= 0:
			time.sleep(args.poll_interval)
			continue

		if sequence in seen_sequences:
			time.sleep(args.poll_interval)
			continue

		observed_at_ms = int(time.time() * 1000)
		latency_ms = observed_at_ms - int(generated_at_ms)
		seen_sequences.add(sequence)

		row = {
			"sample_index": len(rows) + 1,
			"vehicle_id": data.get("vehicle_id", "car01"),
			"sequence": sequence,
			"fault_flag": data.get("fault_flag", 0),
			"generated_at_ms": int(generated_at_ms),
			"middleware_received_at_ms": data.get("middleware_received_at_ms", 0),
			"observed_at_ms": observed_at_ms,
			"end_to_end_latency_ms": latency_ms,
		}
		rows.append(row)
		latencies.append(latency_ms)
		print(f"Sample {len(rows)}/{args.samples}: seq={sequence}, latency_ms={latency_ms}")
		time.sleep(args.poll_interval)

	summary = summarize(latencies)

	csv_path = output_dir / f"latency_samples_{args.label}.csv"
	summary_path = output_dir / f"latency_summary_{args.label}.md"
	write_samples_csv(csv_path, rows)
	write_summary_markdown(summary_path, args.label, summary)

	print("Experiment complete")
	print(f"Samples: {csv_path}")
	print(f"Summary: {summary_path}")
	print(f"Stats: {summary}")


if __name__ == "__main__":
	main()
