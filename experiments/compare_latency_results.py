import argparse
import csv
import statistics
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(description="Compare two latency sample CSV files.")
    parser.add_argument("--baseline", required=True, help="Path to baseline CSV")
    parser.add_argument("--modified", required=True, help="Path to modified CSV")
    parser.add_argument("--output", default="experiments/results/latency_comparison.md", help="Output markdown path")
    return parser.parse_args()


def read_latencies(path):
    latencies = []
    with open(path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            latencies.append(float(row["end_to_end_latency_ms"]))
    if not latencies:
        raise ValueError(f"No latency rows found in {path}")
    return latencies


def stats(latencies):
    return {
        "count": len(latencies),
        "min_ms": round(min(latencies), 2),
        "avg_ms": round(statistics.mean(latencies), 2),
        "p95_ms": round(statistics.quantiles(latencies, n=100)[94], 2) if len(latencies) >= 20 else round(max(latencies), 2),
        "max_ms": round(max(latencies), 2),
    }


def change_pct(old, new):
    if old == 0:
        return "n/a"
    return f"{round(((new - old) / old) * 100, 2)}%"


def render_comparison(baseline_stats, modified_stats):
    lines = [
        "# Latency Comparison (Baseline vs Modified)",
        "",
        "| Metric | Baseline (ms) | Modified (ms) | Change |",
        "|---|---:|---:|---:|",
    ]

    for metric in ["min_ms", "avg_ms", "p95_ms", "max_ms"]:
        lines.append(
            f"| {metric} | {baseline_stats[metric]} | {modified_stats[metric]} | {change_pct(baseline_stats[metric], modified_stats[metric])} |"
        )

    lines.append(f"| sample_count | {baseline_stats['count']} | {modified_stats['count']} | n/a |")
    lines.append("")
    lines.append("```mermaid")
    lines.append("xychart-beta")
    lines.append("    title Average and P95 Latency")
    lines.append("    x-axis [baseline_avg, modified_avg, baseline_p95, modified_p95]")
    lines.append(
        f"    bar [{baseline_stats['avg_ms']}, {modified_stats['avg_ms']}, {baseline_stats['p95_ms']}, {modified_stats['p95_ms']}]"
    )
    lines.append("```")
    lines.append("")
    return "\n".join(lines)


def main():
    args = parse_args()

    baseline_path = Path(args.baseline)
    modified_path = Path(args.modified)
    output_path = Path(args.output)

    baseline_stats = stats(read_latencies(baseline_path))
    modified_stats = stats(read_latencies(modified_path))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(render_comparison(baseline_stats, modified_stats))

    print(f"Comparison written to: {output_path}")


if __name__ == "__main__":
    main()
