import re
import shutil
import sys
from pathlib import Path

root = Path.home() / "LexProof-Pocket"
main_file = root / "backend" / "main.py"
backup_root = root / "backup-before-qvac-integration"

text = main_file.read_text(encoding="utf-8-sig")

if "def add_ai_analysis(extracted_text, result, source_type):" not in text:
    print("STOP: Expected function signature not found. main.py was not changed.")
    sys.exit(2)

pattern = r"(?ms)^def add_ai_analysis\s*\(.*?\)\s*->\s*dict\[str,\s*Any\]:.*?(?=^def\s|\Z)"
match = re.search(pattern, text)
if not match:
    print("STOP: Could not safely identify the function boundaries.")
    sys.exit(3)

replacement = '''def add_ai_analysis(extracted_text, result, source_type):
    """Analyze with local QVAC only; do not silently upload text to a cloud AI."""
    from qvac_analysis import analyze_with_qvac_local

    document_text = (extracted_text or "")[:MAX_TEXT_LENGTH]
    try:
        report = analyze_with_qvac_local(
            document_text=document_text,
            source_type=source_type
        )
        result["ai_status"] = "completed"
        result["ai_report"] = report
        result["document_summary"] = report.get("summary", "")
        result["analysis_type"] = f"qvac_local_{source_type}_analysis"
        result.pop("ai_error", None)
        result.pop("ai_message", None)
    except Exception as exc:
        result["ai_status"] = "unavailable"
        result["ai_report"] = None
        result["ai_message"] = (
            "Local QVAC analysis failed. Preliminary keyword findings may remain "
            "available. No cloud AI fallback was used. Details: " + str(exc)[:500]
        )
        result["analysis_type"] = f"{source_type}_keyword_scan_qvac_unavailable"
'''

new_text = text[:match.start()] + replacement + "\n\n" + text[match.end():]

if new_text == text:
    print("STOP: No change generated.")
    sys.exit(4)

# Verify the existing backup folder is present before writing.
if not backup_root.exists() or not any(backup_root.iterdir()):
    print("STOP: Backup folder not found. main.py was not changed.")
    sys.exit(5)

main_file.write_text(new_text, encoding="utf-8")
print("Patched backend/main.py to use local QVAC.")
print("Existing backup retained in:", backup_root)
