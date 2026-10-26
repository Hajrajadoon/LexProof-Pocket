from pathlib import Path
import ast

for name in ["backend/main.py", "backend/ai_analysis.py"]:
    path = Path(name)
    print(f"\n===== {name} =====")

    if not path.exists():
        print("FILE NOT FOUND")
        continue

    lines = path.read_text(encoding="utf-8-sig").splitlines()
    tree = ast.parse("\n".join(lines), filename=name)

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name in {
                "analyze_with_gemini",
                "add_ai_analysis",
                "analyze_text",
                "analyze_pdf",
                "lifespan",
            }:
                print(f"\n--- {node.name}, lines {node.lineno}-{node.end_lineno} ---")
                print("\n".join(lines[node.lineno - 1:node.end_lineno]))

print("\n===== backend/requirements.txt =====")
p = Path("backend/requirements.txt")
print(p.read_text(encoding="utf-8-sig") if p.exists() else "FILE NOT FOUND")
