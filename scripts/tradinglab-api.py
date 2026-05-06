#!/usr/bin/env python3
"""
tradinglab-api.py — FastAPI server para integración N8N <-> TradingLab

Uso:
    python scripts/tradinglab-api.py

Endpoints:
    GET  /health           — estado del servidor
    GET  /build/status     — cuenta .sq4 en results/
    POST /build/finish     — ejecuta build-finisher.py
    GET  /pipeline/health  — ejecuta system-health-check.py
"""

import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

ROOT    = Path(__file__).parent.parent
SCRIPTS = ROOT / "scripts"

app = FastAPI(title="TradingLab API", version="1.0.0")


# ── Modelos ────────────────────────────────────────────────────────────────

class BuildFinishRequest(BaseModel):
    build: int
    activo: str
    results_folder: str = "results"


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/build/status")
def build_status():
    results_dir = ROOT / "results"
    if not results_dir.exists():
        return {"sq4_count": 0, "files": [], "results_dir": str(results_dir)}

    sq4_files = sorted(results_dir.glob("**/*.sq4"))
    return {
        "sq4_count": len(sq4_files),
        "files": [str(f.relative_to(ROOT)) for f in sq4_files],
        "results_dir": str(results_dir),
    }


@app.post("/build/finish")
def build_finish(req: BuildFinishRequest):
    script = SCRIPTS / "build-finisher.py"
    if not script.exists():
        raise HTTPException(status_code=404, detail=f"Script no encontrado: {script}")

    cmd = [
        sys.executable, str(script),
        "--build",          str(req.build),
        "--activo",         req.activo,
        "--results-folder", req.results_folder,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))

    return {
        "returncode": result.returncode,
        "stdout":     result.stdout[-4000:] if result.stdout else "",
        "stderr":     result.stderr[-1000:] if result.stderr else "",
        "success":    result.returncode == 0,
    }


@app.post("/pipeline/evaluation-gate")
def evaluation_gate():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "build-analyzer.py"), "--no-ollama"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "output": result.stdout[-2000:],
        "errors": result.stderr[-500:]
    }


@app.post("/pipeline/wfo")
def run_wfo():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "build-finisher.py"),
         "--build", "11", "--activo", "XAUUSD",
         "--results-folder", "results/"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "output": result.stdout[-2000:]
    }


@app.post("/pipeline/portfolio")
def run_portfolio():
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "auto-reporter.py"), "--no-ollama"],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "output": result.stdout[-2000:]
    }


@app.post("/sqcli/pipeline")
def sqcli_pipeline(action: str, build: int = 11, activo: str = "XAUUSD"):
    result = subprocess.run(
        [sys.executable, str(SCRIPTS / "sqcli-pipeline.py"),
         f"--{action}", "--build", str(build), "--activo", activo],
        capture_output=True, text=True, cwd=str(ROOT)
    )
    return {
        "status": "ok" if result.returncode == 0 else "error",
        "action": action,
        "output": result.stdout[-2000:]
    }


@app.get("/pipeline/health")
def pipeline_health():
    script = SCRIPTS / "system-health-check.py"
    if not script.exists():
        raise HTTPException(status_code=404, detail=f"Script no encontrado: {script}")

    result = subprocess.run(
        [sys.executable, str(script)],
        capture_output=True, text=True, cwd=str(ROOT)
    )

    return {
        "returncode": result.returncode,
        "output":     result.stdout[-4000:] if result.stdout else "",
        "stderr":     result.stderr[-1000:] if result.stderr else "",
        "success":    result.returncode == 0,
    }


# ── Main ───────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8765, log_level="info")
