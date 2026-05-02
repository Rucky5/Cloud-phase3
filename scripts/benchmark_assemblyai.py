import assemblyai as aai
import time
import os
import json
import psutil
import requests

# ── CONFIG ──────────────────────────────────────────────────────────
aai.settings.api_key = "4adfc90cb0294159b0d265675a7d2388"  # keep your actual key

AUDIO_FILES = {
    "short":  "benchmark_inputs/short.wav",
    "medium": "benchmark_inputs/medium.wav",
    "long":   "benchmark_inputs/large.wav",
}

AUDIO_DURATIONS_MIN = {
    "short":  5.52,
    "medium": 29.57,
    "long":   60.09
}

COST_PER_HOUR = 0.37
RESULTS_DIR   = "benchmark_results"
os.makedirs(RESULTS_DIR, exist_ok=True)

# ── NETWORK LATENCY ──────────────────────────────────────────────────
def measure_latency():
    print("\n🌐 Measuring network latency to AssemblyAI...")
    try:
        latency_start = time.time()
        requests.get(
            "https://api.assemblyai.com/v2",
            headers={"authorization": aai.settings.api_key},
            timeout=10
        )
        latency_end = time.time()
        latency_ms = round((latency_end - latency_start) * 1000, 2)
        print(f"📡 Network latency (RTT): {latency_ms} ms")
        return latency_ms
    except Exception as e:
        print(f"⚠️  Could not measure latency: {e}")
        return None

# ── BENCHMARK ONE FILE ───────────────────────────────────────────────
def benchmark_file(label, filepath):
    print(f"\n🔄 Transcribing [{label.upper()}]: {filepath}")

    if not os.path.exists(filepath):
        print(f"⚠️  File not found: {filepath} — skipping")
        return None

    config = aai.TranscriptionConfig()
    transcriber = aai.Transcriber(config=config)

    cpu_before = psutil.cpu_percent(interval=1)
    start_time = time.time()

    transcript = transcriber.transcribe(filepath)

    end_time  = time.time()
    cpu_after = psutil.cpu_percent(interval=1)

    if transcript.status == aai.TranscriptStatus.error:
        print(f"❌ Error: {transcript.error}")
        return None

    total_time = round(end_time - start_time, 3)
    avg_cpu    = round((cpu_before + cpu_after) / 2, 2)
    duration_s = AUDIO_DURATIONS_MIN[label] * 60
    rtf        = round(total_time / duration_s, 3)
    cost       = round((AUDIO_DURATIONS_MIN[label] / 60) * COST_PER_HOUR, 4)

    result = {
        "label":          label,
        "file":           filepath,
        "inference_time": total_time,
        "avg_cpu_usage":  avg_cpu,
        "rtf":            rtf,
        "cost_usd":       cost,
        "text_preview":   transcript.text[:300] if transcript.text else "",
    }

    print(f"✅ Done in {total_time}s | CPU: {avg_cpu}% | RTF: {rtf} | Cost: ${cost}")
    print(f"📝 Preview: {result['text_preview']}...")
    return result

# ── MAIN ─────────────────────────────────────────────────────────────
latency = measure_latency()

all_results = []
for label, path in AUDIO_FILES.items():
    result = benchmark_file(label, path)
    if result:
        if latency:
            result["network_latency_ms"] = latency
        all_results.append(result)

# Save JSON
output_path = os.path.join(RESULTS_DIR, "assemblyai_results.json")
with open(output_path, "w") as f:
    json.dump(all_results, f, indent=2)
print(f"\n💾 Results saved to {output_path}")

# Summary table
print("\n" + "=" * 65)
print(f"{'Label':<10} {'Time (s)':<15} {'CPU %':<12} {'RTF':<10} {'Cost $'}")
print("-" * 65)
for r in all_results:
    print(f"{r['label']:<10} {r['inference_time']:<15} {r['avg_cpu_usage']:<12} {r['rtf']:<10} {r['cost_usd']}")
print("=" * 65)