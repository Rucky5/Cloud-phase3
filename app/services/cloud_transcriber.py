import os
import time
import tempfile
import psutil
import requests

API_KEY = "4adfc90cb0294159b0d265675a7d2388"
COST_PER_HOUR = 0.37


def measure_latency() -> float | None:
    try:
        start = time.time()
        requests.get(
            "https://api.assemblyai.com/v2",
            headers={"authorization": API_KEY},
            timeout=10,
        )
        return round((time.time() - start) * 1000, 2)
    except Exception:
        return None


def upload_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers={"authorization": API_KEY},
            data=f,
        )
    print("Upload response:", response.status_code, response.text)
    response.raise_for_status()
    return response.json()["upload_url"]


def transcribe(audio) -> dict:
    # Save upload to temp file
    suffix = os.path.splitext(audio.filename)[1] if audio.filename else ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio.file.read())
        tmp_path = tmp.name

    try:
        network_latency = measure_latency()

        # Upload file to AssemblyAI
        upload_url = upload_file(tmp_path)

        # Submit transcription request
        cpu_before = psutil.cpu_percent(interval=1)
        start_time = time.time()

        response = requests.post(
            "https://api.assemblyai.com/v2/transcript",
            headers={
                "authorization": API_KEY,
                "content-type": "application/json"
            },
            json={
                "audio_url": upload_url,
                "speech_models": ["universal-2"]
            }
        )
        print("Transcript response:", response.status_code, response.text)
        transcript_id = response.json()["id"]

        # Poll until complete
        while True:
            poll = requests.get(
                f"https://api.assemblyai.com/v2/transcript/{transcript_id}",
                headers={"authorization": API_KEY}
            )
            result = poll.json()
            if result["status"] == "completed":
                break
            elif result["status"] == "error":
                raise Exception(result["error"])
            time.sleep(2)

        inference_time = round(time.time() - start_time, 3)
        cpu_after = psutil.cpu_percent(interval=1)
        avg_cpu = round((cpu_before + cpu_after) / 2, 2)

        audio_ms = result.get("audio_duration")
        audio_seconds = round(audio_ms, 2) if audio_ms else None
        audio_minutes = round(audio_seconds / 60, 2) if audio_seconds else None
        cost = round((audio_seconds / 3600) * COST_PER_HOUR, 4) if audio_seconds else None

        return {
            "text": result.get("text", ""),
            "inference_time_seconds": inference_time,
            "audio_duration_seconds": audio_seconds,
            "audio_duration_minutes": audio_minutes,
            "avg_cpu_percent": avg_cpu,
            "network_latency_ms": network_latency,
            "cost_usd": cost,
        }
    finally:
        os.remove(tmp_path)