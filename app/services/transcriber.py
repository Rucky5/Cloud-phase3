import tempfile
import time
import shutil
import os
from pathlib import Path

import psutil
import whisper
from whisper import audio as whisper_audio
from fastapi import UploadFile


class TranscriptionError(Exception):
    """Raised when the audio file cannot be transcribed."""


class WhisperTranscriber:
    def __init__(self, model_name: str = "base") -> None:
        self.model_name = model_name
        self._model = None

    @property
    def model(self):
        if self._model is None:
            self._model = whisper.load_model(self.model_name)
        return self._model

    def _resolve_ffmpeg(self) -> str | None:
        ffmpeg_path = shutil.which("ffmpeg")
        if ffmpeg_path:
            return ffmpeg_path

        windows_candidates = [
            Path(r"C:\ffmpeg-8.1-essentials_build\bin\ffmpeg.exe"),
            Path(r"C:\ffmpeg\bin\ffmpeg.exe"),
            Path(r"C:\Program Files\FFmpeg\bin\ffmpeg.exe"),
        ]

        for candidate in windows_candidates:
            if candidate.exists():
                bin_dir = str(candidate.parent)
                current_path = os.environ.get("PATH", "")
                if bin_dir not in current_path:
                    os.environ["PATH"] = f"{bin_dir}{os.pathsep}{current_path}" if current_path else bin_dir
                return str(candidate)

        return None

    def transcribe(self, audio: UploadFile, language: str | None = None) -> dict:
        suffix = Path(audio.filename or "audio.webm").suffix or ".webm"

        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio:
            temp_audio.write(audio.file.read())
            temp_path = Path(temp_audio.name)

        try:
            return self.transcribe_file(temp_path, language)
        finally:
            temp_path.unlink(missing_ok=True)

    def transcribe_file(self, file_path: str | Path, language: str | None = None) -> dict:
        path = Path(file_path)

        if not path.exists():
            raise TranscriptionError(f"Audio file not found: {path}")
        if self._resolve_ffmpeg() is None:
            raise TranscriptionError(
                "FFmpeg is not installed or not available on PATH. Install FFmpeg, then restart the app."
            )

        started_at = time.perf_counter()
        process = psutil.Process()
        cpu_count = psutil.cpu_count(logical=True) or 1
        cpu_start = sum(process.cpu_times()[:2])
        try:
            audio_array = whisper_audio.load_audio(str(path))
        except Exception as exc:
            raise TranscriptionError(
                "Could not read the uploaded audio. Check that FFmpeg is installed and the file format is supported."
            ) from exc
        duration_seconds = len(audio_array) / whisper_audio.SAMPLE_RATE
        duration_minutes = duration_seconds / 60.0

        try:
            response = self.model.transcribe(str(path), language=language or None)
        except Exception as exc:
            raise TranscriptionError(
                "Transcription failed. Check that FFmpeg is installed and the audio format is supported."
            ) from exc

        inference_time_seconds = time.perf_counter() - started_at
        cpu_end = sum(process.cpu_times()[:2])
        cpu_delta = max(cpu_end - cpu_start, 0.0)
        avg_cpu_percent = round((cpu_delta / max(inference_time_seconds, 1e-6)) * 100 / cpu_count, 2)

        return {
            "text": response.get("text", "").strip(),
            "language": response.get("language", language or "unknown"),
            "segments": response.get("segments", []),
            "model": self.model_name,
            "inference_time_seconds": round(inference_time_seconds, 3),
            "avg_cpu_percent": avg_cpu_percent,
            "audio_duration_seconds": round(duration_seconds, 2),
            "audio_duration_minutes": round(duration_minutes, 2),
        }
