# NTRO SIGINT RF Signal Analysis Suite

This is the combined frontend + backend application.

## Structure

- `frontend/` — React + Vite interface
- `backend/` — FastAPI RF analysis engine
- `backend/models/modulation_model.pkl` — trained modulation classifier
- `backend/src/` — DSP, ML, signal generation and demodulation pipeline

## Important: no default frontend sample data

The original frontend contained hard-coded satellite sessions and generated PSD/constellation/bitstream examples. Those have been removed.

The UI starts empty. A user must upload a `.iq` or `.wav` capture. Results displayed in the spectral, parameter, constellation and bitstream modules come from the backend analysis.

## Backend pipeline

`IQ/WAV -> universal reader -> DSP analysis -> 23 features -> Random Forest -> DSP+ML evidence fusion -> demodulation`

Supported modulation labels in the trained model:

`BPSK, QPSK, 8PSK, 16QAM, FSK, GFSK, AM, FM`

## Run backend

Windows PowerShell:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

Health check: `http://localhost:8000/health`

## Run frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`).

The frontend defaults to the backend at `http://localhost:8000`. To change it:

Create `frontend/.env`:

```text
VITE_API_URL=http://localhost:8000
```

For a deployed frontend/backend, set `VITE_API_URL` to the deployed FastAPI URL and set the backend environment variable:

```text
FRONTEND_ORIGINS=https://your-frontend.example.com
```

## Uploading files

- `.wav`: sample rate is read from the WAV header.
- raw `.iq`: because raw IQ has no standard header, enter the sample rate in MHz in the ingestion panel before uploading.
- Center frequency, satellite ID and orbital regime are optional display metadata; they do not replace backend signal measurements.

## Current backend limitations

The existing backend does not implement FEC decoding or preamble correlation endpoints. The merged frontend therefore does not display fabricated FEC/BER/correlation values. It explicitly reports those capabilities as unavailable instead of showing sample values.
