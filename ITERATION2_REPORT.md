# Iteration 2 Report

## 1. Implemented System Extension

Describe what was changed from Iteration 1.

Implemented in this repository:
- Middleware drop and delay fault injection in middleware/zenoh_subscriber.py
- Telemetry timestamp and sequence instrumentation across simulator/middleware/ditto/diagnostics
- Configurable simulator update interval for higher-rate load scenarios

## 2. Architecture Impact

State whether architecture changed significantly.

- Architecture change level: Moderate
- Added behavior in middleware and telemetry metadata propagation

Updated architecture reference:
- See README.md section "Updated Architecture (Iteration 2)"

## 3. Functional Validation Evidence

Provide evidence that the modified system still works correctly.

Suggested evidence to include:
- Simulator log sample showing sequence and generated_at_ms
- Middleware subscriber log sample showing drop/delay behavior
- Ditto updater log sample showing updates
- Diagnostics API response from /diagnostics/state
- Output of: python experiments/validate_pipeline.py --samples 10

## 4. Non-Functional Experiment Design

Measured metric:
- End-to-end latency from generated_at_ms to observation at Ditto read time

Experiment setup:
1. Baseline: ZENOH_DROP_PROB=0.0, ZENOH_DELAY_MS=0
2. Modified: ZENOH_DROP_PROB=0.20, ZENOH_DELAY_MS=150
3. Sample count per run: 30

Commands:
- python experiments/run_latency_experiment.py --label baseline --samples 30
- python experiments/run_latency_experiment.py --label fault_injection --samples 30
- python experiments/compare_latency_results.py --baseline experiments/results/latency_samples_baseline.csv --modified experiments/results/latency_samples_fault_injection.csv --output experiments/results/latency_comparison.md

## 5. Results Table

Fill this table using experiments/results/latency_comparison.md

| Metric | Baseline (ms) | Modified (ms) | Change |
|---|---:|---:|---:|
| min_ms | [fill] | [fill] | [fill] |
| avg_ms | [fill] | [fill] | [fill] |
| p95_ms | [fill] | [fill] | [fill] |
| max_ms | [fill] | [fill] | [fill] |
| sample_count | [fill] | [fill] | n/a |

## 6. Analysis

Answer the following briefly:

1. How did the system behave before and after the modification?
- [fill]

2. What changed in the measured metric?
- [fill]

3. Why did these changes occur?
- [fill]

4. Any reliability observations (drops, stale state, slower updates)?
- [fill]

## 7. Demo Video Checklist (3-5 minutes)

Include in the video:
- Running pipeline components
- Baseline scenario and output
- Fault injection scenario and output
- Generated result files in experiments/results/
- Brief conclusion and interpretation

## 8. Repository and Submission Checklist

- Iteration 2 code committed to same repository used for Iteration 1
- README updated with reproduction steps
- TA collaborator added: zubxxr
- Report completed and included
