# Whisper SST Demo

This project is a simple speech-to-text system for Phase 2 using OpenAI Whisper. It includes:

- A FastAPI backend
- A small web interface
- Audio file upload
- Whisper-based transcription output

## Project Structure

```text
SWE486/
|-- app/
|   |-- main.py
|   `-- services/transcriber.py
|-- static/
|   |-- app.js
|   `-- styles.css
|-- templates/
|   `-- index.html
|-- requirements.txt
`-- README.md
```

## Requirements

1. Python 3.10 or newer
2. FFmpeg installed and available in your system path

## Installation

```bash
pip install -r requirements.txt
```

## Run the App

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000
```

## How It Works

1. The user uploads an audio file.
2. The frontend sends the file to `/api/transcribe`.
3. The backend saves the file temporarily.
4. Whisper transcribes the speech into text.
5. The result is returned and shown in the browser.

## Suggested Phase 2 Description

You can describe your Phase 2 work like this:

> We implemented a speech-to-text module using OpenAI Whisper. The system accepts uploaded audio files, processes them on the backend, and returns the transcribed text through a web interface. This allows users to convert spoken language into written text in an easy and interactive way.

## Notes

- The first transcription may take a little longer because the Whisper model loads on first use.
- You can change the model size in `app/services/transcriber.py` from `base` to `tiny`, `small`, or another supported Whisper model.

## Phase 2 Benchmarking

To satisfy the local inference part of Phase 2:

1. Put three audio files in `benchmark_inputs/`.
2. Use these sizes:
   - Short: 5 to 10 seconds
   - Medium: 15 to 30 seconds
   - Large: 45 to 60 seconds
3. Run:

```bash
python scripts/system_info.py
python scripts/benchmark_whisper.py --audio-dir benchmark_inputs --language en
```

This creates:

- `benchmark_results/system_info.json`
- `benchmark_results/inference_results.csv`

For energy usage, run the benchmark while Intel Power Gadget or another local power profiler is open, then copy the readings into `benchmark_results/REPORT_TEMPLATE.md`.
