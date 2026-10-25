import json
import subprocess
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
QVAC_HOME = Path.home() / "qvac-compat-test"
QVAC_PYTHON = QVAC_HOME / ".venv" / "Scripts" / "python.exe"
QVAC_WORKER = APP_DIR / "qvac_local_worker.py"

MAX_ATTEMPTS = 1          # the worker already retries internally
TIMEOUT_SECONDS = 400


def analyze_with_qvac_local(
    document_text: str,
    source_type: str = "pdf",
) -> dict:
    if not QVAC_PYTHON.exists():
        raise RuntimeError(
            f"QVAC Python environment not found at {QVAC_PYTHON}"
        )

    if not document_text or not document_text.strip():
        raise ValueError("No document text was available for analysis.")

    payload = json.dumps(
        {"document_text": document_text[:6000]},
        ensure_ascii=False,
    )

    last_error = "No diagnostic output"

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            completed = subprocess.run(
                [str(QVAC_PYTHON), str(QVAC_WORKER)],
                input=payload,
                text=True,
                capture_output=True,
                timeout=TIMEOUT_SECONDS,
                cwd=str(QVAC_HOME),
                encoding="utf-8",
                errors="replace",
            )

            for line in reversed(completed.stdout.splitlines()):
                if line.startswith("LEXPROOF_QVAC_RESULT="):
                    try:
                        result = json.loads(line.split("=", 1)[1])
                        if isinstance(result, dict):
                            return result
                        last_error = "QVAC result was not a JSON object."
                    except json.JSONDecodeError as exc:
                        last_error = f"Invalid result JSON: {exc}"
                    break
            else:
                # Keep only meaningful stderr lines (drop llama.cpp noise).
                useful = [
                    line for line in completed.stderr.splitlines()
                    if line.strip()
                    and not line.startswith(("repack:", "cmn", "parse:"))
                    and "common_fit_params" not in line
                ]
                last_error = (
                    f"Worker exit {completed.returncode}:\n"
                    + "\n".join(useful[-15:])
                )

        except subprocess.TimeoutExpired:
            last_error = f"QVAC timed out after {TIMEOUT_SECONDS}s."
        except (subprocess.SubprocessError, OSError) as exc:
            last_error = f"{type(exc).__name__}: {exc}"

        if attempt < MAX_ATTEMPTS:
            print("QVAC attempt failed; retrying...")

    raise RuntimeError(f"QVAC local analysis failed: {last_error}")