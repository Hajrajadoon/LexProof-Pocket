import json
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
QVAC_PYTHON = Path.home() / "qvac-compat-test" / ".venv" / "Scripts" / "python.exe"
QVAC_WORKER = APP_DIR / "qvac_local_worker.py"

def analyze_with_qvac_local(document_text: str, source_type: str = "pdf") -> dict:
    if not QVAC_PYTHON.exists():
        raise RuntimeError("Tested QVAC Python environment was not found.")
    payload = json.dumps({
        "document_text": (document_text or "")[:6000]
    }, ensure_ascii=False)

    completed = subprocess.run(
        [str(QVAC_PYTHON), str(QVAC_WORKER)],
        input=payload,
        text=True,
        capture_output=True,
        timeout=300,
        cwd=str(Path.home() / "qvac-compat-test"),
        encoding="utf-8",
        errors="replace",
    )

    for line in reversed(completed.stdout.splitlines()):
        if line.startswith("LEXPROOF_QVAC_RESULT="):
            return json.loads(line.split("=", 1)[1])

    combined = completed.stdout + "\n" + completed.stderr
    error = next(
        (line.split("LEXPROOF_QVAC_ERROR=", 1)[-1]
         for line in reversed(combined.splitlines())
         if "LEXPROOF_QVAC_ERROR=" in line),
        combined[-1200:] or "No diagnostic output"
    )
    raise RuntimeError(
        f"QVAC local analysis failed (exit {completed.returncode}): {error}"
    )
