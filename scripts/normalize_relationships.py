from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path
from typing import Any

from scripts.normalize_entities import normalize_node_label


RELATIONSHIP_LABELS = {
    "assassina": "killed",
    "assassinado por": "killed_by",
    "casado": "spouse_of",
    "casada": "spouse_of",
    "consorte": "consort_of",
    "equivalente": "equivalent_to",
    "filha": "child_of",
    "filho": "child_of",
    "fundou": "founded",
    "irmã": "sibling_of",
    "irma": "sibling_of",
    "irmão": "sibling_of",
    "irmao": "sibling_of",
    "mãe": "parent_of",
    "mae": "parent_of",
    "matou": "killed",
    "pai": "parent_of",
    "participou": "participated_in",
    "pertence": "belongs_to_group",
    "rei": "ruled",
    "rainha": "ruled",
}


def _slug_from_external_id(external_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", external_id).strip("-") or external_id


def _node_entity_ids(nodes: list[dict[str, Any]]) -> set[str]:
    entity_ids: set[str] = set()
    for node in nodes:
        label = normalize_node_label(str(node.get("label") or node.get("value") or ""))
        if label:
            entity_ids.add(_slug_from_external_id(str(node["id"])))
    return entity_ids


def _node_by_id(nodes: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(node["id"]): node for node in nodes}


def _is_entity_node(node: dict[str, Any] | None) -> bool:
    if node is None:
        return False
    return bool(normalize_node_label(str(node.get("label") or node.get("value") or "")))


def _is_rhombus_connector(node: dict[str, Any] | None) -> bool:
    if node is None or _is_entity_node(node):
        return False
    return "rhombus" in str(node.get("style") or "")


def relationship_type_from_label(label: str, style: str = "") -> str:
    normalized = normalize_node_label(label).lower()
    if normalized in RELATIONSHIP_LABELS:
        return RELATIONSHIP_LABELS[normalized]
    if not normalized and _is_direct_parent_arrow(style):
        return "parent_of"
    return "associated_with"


def _is_direct_parent_arrow(style: str) -> bool:
    if "dashed=1" in style:
        return False
    return "endArrow=classic" in style or "edgeStyle=none" in style or "edgeStyle=orthogonalEdgeStyle" in style


def _notes_for_direct_edge(label: str, style: str) -> str:
    if label:
        return f"Original label: {label}"
    if _is_direct_parent_arrow(style):
        return "Inferred from direct arrow"
    return ""


def normalize_edges(raw: dict[str, Any]) -> list[dict[str, str]]:
    nodes = raw.get("nodes", [])
    edges = raw.get("edges", [])
    entity_ids = _node_entity_ids(nodes)
    nodes_by_id = _node_by_id(nodes)
    relationships: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if not source or not target:
            continue

        source_entity_id = _slug_from_external_id(str(source))
        target_entity_id = _slug_from_external_id(str(target))
        if source_entity_id not in entity_ids or target_entity_id not in entity_ids:
            continue

        label = normalize_node_label(str(edge.get("label") or edge.get("value") or ""))
        style = str(edge.get("style") or "")
        relationship = {
            "id": str(edge["id"]),
            "source_entity_id": source_entity_id,
            "target_entity_id": target_entity_id,
            "relationship_type": relationship_type_from_label(label, style),
            "certainty": "traditional",
            "variant_group": "",
            "notes": _notes_for_direct_edge(label, style),
            "source_id": "",
        }
        relationships.append(relationship)
        seen_ids.add(relationship["id"])

    incoming_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
    outgoing_edges: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        if edge.get("target"):
            incoming_edges[str(edge["target"])].append(edge)
        if edge.get("source"):
            outgoing_edges[str(edge["source"])].append(edge)

    for connector_id, node in nodes_by_id.items():
        if not _is_rhombus_connector(node):
            continue
        incoming = incoming_edges.get(connector_id, [])
        outgoing = outgoing_edges.get(connector_id, [])
        for parent_edge in incoming:
            parent_id = parent_edge.get("source")
            if not parent_id or not _is_entity_node(nodes_by_id.get(str(parent_id))):
                continue
            for child_edge in outgoing:
                child_id = child_edge.get("target")
                if not child_id or not _is_entity_node(nodes_by_id.get(str(child_id))):
                    continue
                relationship_id = f"{connector_id}-{parent_edge['id']}-{child_edge['id']}"
                if relationship_id in seen_ids:
                    continue
                relationships.append(
                    {
                        "id": relationship_id,
                        "source_entity_id": _slug_from_external_id(str(parent_id)),
                        "target_entity_id": _slug_from_external_id(str(child_id)),
                        "relationship_type": "parent_of",
                        "certainty": "traditional",
                        "variant_group": "",
                        "notes": f"Inferred from rhombus connector: {connector_id}",
                        "source_id": "",
                    }
                )
                seen_ids.add(relationship_id)

    return relationships


def _write_csv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_file(
    input_path: str | Path = "data/parsed/drawio_raw.json",
    relationships_path: str | Path = "data/seed/relationships.csv",
) -> list[dict[str, str]]:
    raw = json.loads(Path(input_path).read_text(encoding="utf-8"))
    relationships = normalize_edges(raw)
    _write_csv(
        relationships_path,
        relationships,
        [
            "id",
            "source_entity_id",
            "target_entity_id",
            "relationship_type",
            "certainty",
            "variant_group",
            "notes",
            "source_id",
        ],
    )
    return relationships


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize draw.io edges into relationship seed CSV.")
    parser.add_argument("--input", default="data/parsed/drawio_raw.json")
    parser.add_argument("--relationships-output", default="data/seed/relationships.csv")
    args = parser.parse_args()
    normalize_file(args.input, args.relationships_output)


if __name__ == "__main__":
    main()
