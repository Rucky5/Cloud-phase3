from pathlib import Path

from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.services.power_reader import read_power_stats
from app.services.transcriber import TranscriptionError, WhisperTranscriber


BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(
    title="Whisper SST Demo",
 
)
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

transcriber = WhisperTranscriber()


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/transcribe")
async def transcribe_audio(
    audio: UploadFile = File(...),
    language: str | None = Form(default=None),
) -> JSONResponse:
    try:
        result = transcriber.transcribe(audio, language)
    except TranscriptionError as exc:
        return JSONResponse(status_code=400, content={"error": str(exc)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"error": "Unexpected server error while transcribing audio."},
        )

    power_stats = read_power_stats()
    if power_stats:
        result.update(power_stats)

    return JSONResponse(content=result)
