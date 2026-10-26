from pathlib import Path

p = Path("backend/apply_qvac_patch.py")
s = p.read_text(encoding="utf-8-sig")

old = r'(?ms)^def add_ai_analysis\(extracted_text,\s*result,\s*source_type\):.*?(?=^def\s|\Z)'
new = r'(?ms)^def add_ai_analysis\s*\(.*?\)\s*->\s*dict\[str,\s*Any\]:.*?(?=^def\s|\Z)'

if old not in s:
    print("STOP: Expected old pattern not found. No patch script changes made.")
    raise SystemExit(2)

p.write_text(s.replace(old, new, 1), encoding="utf-8")
print("Patch matching rule updated.")
