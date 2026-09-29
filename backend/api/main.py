"""
FastAPI backend for the RF signal analysis prototype.

Run with:
    python -m uvicorn api.main:app --reload

Endpoints implement Section 20 of the design brief. Results are cached
in-memory (RESULTS dict) keyed by an analysis id -- fine for a hackathon
demo, would be a database in production.
"""
from __future__ import annotations
import sys
import uuid
import os
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.pipeline.analyzer import analyze_file, DEFAULT_MODEL_PATH
from src.io.universal_reader import load_signal
from src.dsp.psd import compute_psd
from src.dsp.spectrogram import compute_spectrogram

app = FastAPI(title="RF Signal Analysis API", version="0.1.0")
FRONTEND_ORIGINS = [x.strip() for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",") if x.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=FRONTEND_ORIGINS,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = PROJECT_ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

RESULTS: dict[str, dict] = {}
FILES: dict[str, Path] = {}


@app.get("/health")
def health():
    model_ready = DEFAULT_MODEL_PATH.exists()
    return {"status": "ok", "model_loaded": model_ready}


@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".iq", ".wav"):
        raise HTTPException(400, "Only .iq and .wav files are supported")
    file_id = str(uuid.uuid4())[:8]
    dest = UPLOAD_DIR / f"{file_id}{suffix}"
    with open(dest, "wb") as f:
        f.write(await file.read())
    FILES[file_id] = dest
    return {"file_id": file_id, "filename": file.filename}


@app.post("/analyze")
def analyze(file_id: str = Form(...), sample_rate_hz: float | None = Form(None),
            wideband: bool = Form(False)):
    if file_id not in FILES:
        raise HTTPException(404, "Unknown file_id -- upload first")
    path = FILES[file_id]
    result = analyze_file(path, assumed_sample_rate_hz=sample_rate_hz, wideband=wideband)
    analysis_id = str(uuid.uuid4())[:8]
    RESULTS[analysis_id] = {"result": result, "path": path, "sample_rate_hz": sample_rate_hz}
    return {"analysis_id": analysis_id, **result}


@app.get("/result/{analysis_id}")
def get_result(analysis_id: str):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    return RESULTS[analysis_id]["result"]


@app.get("/spectrum/{analysis_id}")
def get_spectrum(analysis_id: str):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    path = RESULTS[analysis_id]["path"]
    sr_hint = RESULTS[analysis_id].get("sample_rate_hz")
    loaded = load_signal(path, assumed_sample_rate_hz=sr_hint)
    if loaded.sample_rate_hz is None:
        raise HTTPException(422, "Sample rate unknown for this file")
    freqs, psd_db = compute_psd(loaded.iq, loaded.sample_rate_hz)
    step = max(1, len(freqs) // 2000)
    return {"frequencies_hz": freqs[::step].tolist(), "power_db": psd_db[::step].round(2).tolist()}


@app.get("/spectrogram/{analysis_id}")
def get_spectrogram(analysis_id: str):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    path = RESULTS[analysis_id]["path"]
    sr_hint = RESULTS[analysis_id].get("sample_rate_hz")
    loaded = load_signal(path, assumed_sample_rate_hz=sr_hint)
    if loaded.sample_rate_hz is None:
        raise HTTPException(422, "Sample rate unknown for this file")
    return compute_spectrogram(loaded.iq, loaded.sample_rate_hz)


@app.get("/constellation/{analysis_id}")
def get_constellation(analysis_id: str, signal_index: int = 0, max_points: int = 3000):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    result = RESULTS[analysis_id]["result"]
    if signal_index >= len(result["signals"]):
        raise HTTPException(404, "signal_index out of range")

    path = RESULTS[analysis_id]["path"]
    loaded = load_signal(path)
    iq = loaded.iq
    step = max(1, len(iq) // max_points)
    iq_ds = iq[::step]
    power = float((abs(iq_ds) ** 2).mean()) or 1.0
    iq_norm = iq_ds / (power ** 0.5)

    return {
        "raw_iq": {"i": iq_ds.real.tolist(), "q": iq_ds.imag.tolist()},
        "normalized_iq": {"i": iq_norm.real.tolist(), "q": iq_norm.imag.tolist()},
    }


@app.get("/signals/{analysis_id}")
def get_signals(analysis_id: str):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    return {"signals": RESULTS[analysis_id]["result"]["signals"]}


@app.post("/demodulate/{analysis_id}")
def demodulate(analysis_id: str, signal_index: int = Form(0)):
    if analysis_id not in RESULTS:
        raise HTTPException(404, "Unknown analysis_id")
    result = RESULTS[analysis_id]["result"]
    if signal_index >= len(result["signals"]):
        raise HTTPException(404, "signal_index out of range")
    return result["signals"][signal_index]["demodulation"]
