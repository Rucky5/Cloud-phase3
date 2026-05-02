from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.services.cloud_transcriber import transcribe

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

app = FastAPI(title="AssemblyAI Cloud STT Demo")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("cloud_index.html", {"request": request})


@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)) -> JSONResponse:
    try:
        result = transcribe(audio)
    except Exception as exc:
        return JSONResponse(status_code=500, content={"error": str(exc)})
    return JSONResponse(content=result)