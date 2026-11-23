#!/usr/bin/env python3
"""Apply notebook formatting actions for experiment notebooks.

Examples:
    python tools/notebook_actions.py Ideales_und_reales_Gas
    python tools/notebook_actions.py Vakuum --action split-sections
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


TITLE_PATTERNS = {
    "versuchsbeschreibung": (
        "**V E R S U C H S B E S C H R E I B U N G**",
        "*Fügen Sie Ihre Versuchsbeschreibung hier ein.",
    ),
    "loesung": (
        "**L Ö S U N G**",
        "*Fügen Sie numerische Berechnungen zur Lösung dieser Aufgabe hier ein.",
    ),
    "diskussion": (
        "**D I S K U S S I O N**",
        "*Fügen Sie eine abschließende Diskussion und Bewertung Ihrer Lösung hier ein.",
    ),
}


def resolve_notebook_path(name: str, root: Path | None = None) -> Path:
    root = root or Path(__file__).resolve().parent.parent
    return root / name / "notebooks" / f"{name}.ipynb"


def split_section_cells(notebook: dict[str, Any]) -> tuple[dict[str, Any], int]:
    """Split old placeholder markdown cells into title + separator cells."""
    new_cells: list[dict[str, Any]] = []
    changed = 0

    for cell in notebook.get("cells", []):
        if cell.get("cell_type") != "markdown":
            new_cells.append(cell)
            continue

        source = "".join(cell.get("source", []))
        if not source:
            new_cells.append(cell)
            continue

        for marker, placeholder in TITLE_PATTERNS.values():
            if source.startswith(marker) and placeholder in source:
                new_cells.append(
                    {
                        "cell_type": "markdown",
                        "metadata": dict(cell.get("metadata", {})),
                        "source": [f"{marker}\n"],
                    }
                )
                new_cells.append(
                    {
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": ["---\n"],
                    }
                )
                changed += 1
                break
        else:
            new_cells.append(cell)

    notebook["cells"] = new_cells
    return notebook, changed


def apply_action(notebook_path: Path, action: str) -> int:
    with notebook_path.open("r", encoding="utf-8") as handle:
        notebook = json.load(handle)

    if action == "split-sections":
        notebook, changed = split_section_cells(notebook)
    else:
        raise ValueError(f"Unsupported action: {action}")

    if changed:
        with notebook_path.open("w", encoding="utf-8") as handle:
            json.dump(notebook, handle, indent=1, ensure_ascii=False)
            handle.write("\n")

    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("name", help="Experiment name, e.g. Ideales_und_reales_Gas")
    parser.add_argument(
        "--action",
        default="split-sections",
        help="Notebook action to apply (default: split-sections)",
    )
    args = parser.parse_args()

    notebook_path = resolve_notebook_path(args.name)
    if not notebook_path.exists():
        raise FileNotFoundError(f"Notebook not found: {notebook_path}")

    changed = apply_action(notebook_path, args.action)
    print(f"Updated {changed} matching markdown cells in {notebook_path}")


if __name__ == "__main__":
    main()
