from __future__ import annotations

import argparse
import html
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")


def clean_label(value: str | None) -> str:
    if not value:
        return ""
    decoded = html.unescape(value)
    without_tags = TAG_RE.sub(" ", decoded)
    normalized = re.sub(r"\s*/\s*", "/", without_tags)
    return re.sub(r"\s+", " ", normalized).strip()


def _float_or_none(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _geometry(cell: ET.Element) -> dict[str, float | str | None]:
    geometry = cell.find("mxGeometry")
    if geometry is None:
        return {}
    result: dict[str, float | str | None] = {}
    for key in ("x", "y", "width", "height"):
        result[key] = _float_or_none(geometry.get(key))
    if geometry.get("relative") is not None:
        result["relative"] = geometry.get("relative")
    return {key: value for key, value in result.items() if value is not None}


def _cell_payload(cell: ET.Element, page: dict[str, str | None]) -> dict[str, Any]:
    return {
        "id": cell.get("id"),
        "value": cell.get("value") or "",
        "label": clean_label(cell.get("value")),
        "style": cell.get("style") or "",
        "parent": cell.get("parent"),
        "source": cell.get("source"),
        "target": cell.get("target"),
        "page_id": page["id"],
        "page_name": page["name"],
        "geometry": _geometry(cell),
    }


def parse_drawio_file(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    tree = ET.parse(source)
    root = tree.getroot()
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    pages: list[dict[str, str | None]] = []

    diagrams = root.findall(".//diagram") if root.tag == "mxfile" else [root]
    for index, diagram in enumerate(diagrams):
        page = {
            "id": diagram.get("id") or f"page-{index + 1}",
            "name": diagram.get("name") or f"Page {index + 1}",
        }
        pages.append(page)
        graph_root = diagram.find(".//root") if diagram.tag == "diagram" else diagram.find(".//root")
        if graph_root is None:
            continue

        for cell in graph_root.findall("mxCell"):
            if cell.get("vertex") == "1":
                nodes.append(_cell_payload(cell, page))
            elif cell.get("edge") == "1":
                edges.append(_cell_payload(cell, page))

    return {
        "source_file": str(source),
        "pages": pages,
        "nodes": nodes,
        "edges": edges,
    }


def write_json(data: dict[str, Any], output_path: str | Path) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse a draw.io file into raw JSON.")
    parser.add_argument("input", help="Path to the .drawio file.")
    parser.add_argument(
        "--output",
        default="data/parsed/drawio_raw.json",
        help="Output JSON path.",
    )
    args = parser.parse_args()

    write_json(parse_drawio_file(args.input), args.output)


if __name__ == "__main__":
    main()
