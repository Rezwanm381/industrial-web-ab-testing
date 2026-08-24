"""Execute the two trusted development notebooks without external notebook tooling."""

from __future__ import annotations

import contextlib
import io
import json
import os
import traceback
from pathlib import Path


ROOT = Path(__file__).resolve().parent


def execute_notebook(path: Path) -> None:
    notebook = json.loads(path.read_text(encoding="utf-8"))
    namespace = {"__name__": "__main__"}
    execution_count = 0
    original_directory = Path.cwd()
    os.chdir(ROOT)
    try:
        for cell in notebook.get("cells", []):
            if cell.get("cell_type") != "code":
                continue
            execution_count += 1
            cell["execution_count"] = execution_count
            stream = io.StringIO()
            try:
                with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
                    exec(compile("".join(cell.get("source", [])), str(path), "exec"), namespace)
            except Exception:
                stream.write(traceback.format_exc())
                cell["outputs"] = [
                    {"name": "stdout", "output_type": "stream", "text": [stream.getvalue()]}
                ]
                raise
            output = stream.getvalue()
            cell["outputs"] = (
                [{"name": "stdout", "output_type": "stream", "text": [output]}]
                if output
                else []
            )
    finally:
        os.chdir(original_directory)
    notebook["metadata"]["execution"] = {
        "status": "completed",
        "runner": "execute_notebooks.py",
    }
    path.write_text(json.dumps(notebook, indent=1), encoding="utf-8")
    print(f"Executed {path.name}: {execution_count} code cells")


def main() -> None:
    for name in ("01_experiment_overview.ipynb", "02_ab_analysis.ipynb"):
        execute_notebook(ROOT / "notebooks" / name)


if __name__ == "__main__":
    main()

