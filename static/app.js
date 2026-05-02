const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const inferenceTimeEl = document.getElementById("inferenceTime");
const audioDurationEl = document.getElementById("audioDuration");
const avgCpuEl = document.getElementById("avgCpu");
const fileInput = document.getElementById("fileInput");
const copyButton = document.getElementById("copyButton");

function setStatus(message) {
  statusEl.textContent = message;
}

function setResult(data) {
  resultEl.value = data.text || "";
  const inference = data.inference_time_seconds ?? "--";
  const audioSeconds = data.audio_duration_seconds ?? null;
  const audioMinutes = data.audio_duration_minutes ?? null;
  const avgCpu = data.avg_cpu_percent ?? "--";

  inferenceTimeEl.textContent = inference;
  if (audioSeconds !== null && audioMinutes !== null) {
    audioDurationEl.textContent = `${audioSeconds} seconds (${audioMinutes} min)`;
  } else {
    audioDurationEl.textContent = "--";
  }
  avgCpuEl.textContent = avgCpu;
}

async function uploadAudio(blob, filename) {
  const formData = new FormData();
  formData.append("audio", blob, filename);

  setStatus("Transcribing audio...");

  const response = await fetch("/api/transcribe", {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.error || "Transcription failed.");
  }

  setResult(data);
  setStatus("Transcription completed.");
}

fileInput.addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) {
    return;
  }

  try {
    await uploadAudio(file, file.name);
  } catch (error) {
    setStatus(error.message);
  } finally {
    fileInput.value = "";
  }
});

copyButton.addEventListener("click", async () => {
  await navigator.clipboard.writeText(resultEl.value);
  setStatus("Transcription copied to clipboard.");
});
