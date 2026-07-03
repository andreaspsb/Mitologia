from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path
from typing import Any


TAG_RE = re.compile(r"<[^>]+>")
ROMAN_ALIASES = {
    "Baco",
    "Ceres",
    "Cupido",
    "Diana",
    "Hercules",
    "Hércules",
    "Juno",
    "Júpiter",
    "Marte",
    "Mercúrio",
    "Minerva",
    "Netuno",
    "Plutão",
    "Proserpina",
    "Saturno",
    "Terra",
    "Urano",
    "Vênus",
    "Vesta",
    "Vulcano",
}
OLYMPIANS = {
    "Afrodite",
    "Apolo",
    "Ares",
    "Ártemis",
    "Atena",
    "Deméter",
    "Dioniso",
    "Hades",
    "Hefesto",
    "Hera",
    "Hermes",
    "Héstia",
    "Poseidon",
    "Zeus",
}
MONSTER_TERMS = {
    "cérbero",
    "dragão",
    "hidra",
    "javali",
    "leão",
    "minotauro",
    "monstro",
    "quimera",
    "serpente",
    "tifão",
}
OBJECT_TERMS = {
    "cinto",
    "gado",
    "genitálias",
    "maçãs",
    "raio",
}
PLACE_TERMS = {
    "abismo",
    "atenas",
    "céu",
    "egito",
    "mar",
    "montanhas",
    "olimpo",
    "submundo",
    "tártaro",
    "troia",
}
EVENT_TERMS = {
    "castração",
    "guerra",
    "jornada",
    "separação",
    "titanomaquia",
}
GROUP_TERMS = {
    "aves",
    "gigantes",
    "melíades",
    "musas",
    "ninfas",
    "sátiros",
}


def normalize_node_label(label: str) -> str:
    decoded = html.unescape(label or "")
    without_tags = TAG_RE.sub(" ", decoded)
    normalized = re.sub(r"\s*/\s*", " / ", without_tags)
    return re.sub(r"\s+", " ", normalized).strip()


def infer_entity_type(label: str) -> str:
    normalized = normalize_node_label(label)
    lowered = normalized.lower()
    primary_name = normalized.split("/")[0].strip()

    if primary_name in OLYMPIANS:
        return "olympian"
    if "rei " in lowered or lowered.startswith("rei ") or "rainha" in lowered:
        return "king"
    if "náiade" in lowered or "ninfa" in lowered:
        return "nymph"
    if any(term in lowered for term in EVENT_TERMS):
        return "event"
    if any(term in lowered for term in MONSTER_TERMS):
        return "monster"
    if any(term in lowered for term in OBJECT_TERMS):
        return "object"
    if any(term in lowered for term in PLACE_TERMS):
        return "place"
    if any(term in lowered for term in GROUP_TERMS):
        return "group"
    return "unknown"


def _slug_from_external_id(external_id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]+", "-", external_id).strip("-") or external_id


def _alias_type(alias: str) -> str:
    return "roman" if alias in ROMAN_ALIASES else "alternate"


def normalize_nodes(nodes: list[dict[str, Any]]) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    entities: list[dict[str, str]] = []
    aliases: list[dict[str, str]] = []

    for node in nodes:
        label = normalize_node_label(str(node.get("label") or node.get("value") or ""))
        if not label:
            continue

        parts = [part.strip() for part in label.split("/") if part.strip()]
        name = parts[0]
        external_id = str(node["id"])
        entity_id = _slug_from_external_id(external_id)
        entities.append(
            {
                "id": entity_id,
                "external_id": external_id,
                "name": name,
                "canonical_name": name,
                "entity_type": infer_entity_type(label),
                "gender": "",
                "description": "",
                "notes": "",
            }
        )

        for index, alias in enumerate(parts[1:], start=1):
            aliases.append(
                {
                    "id": f"{entity_id}-alias-{index}",
                    "entity_id": entity_id,
                    "alias": alias,
                    "language": "",
                    "alias_type": _alias_type(alias),
                    "notes": "",
                }
            )

    return entities, aliases


def _write_csv(path: str | Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def normalize_file(
    input_path: str | Path = "data/parsed/drawio_raw.json",
    entities_path: str | Path = "data/seed/entities.csv",
    aliases_path: str | Path = "data/seed/aliases.csv",
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    raw = json.loads(Path(input_path).read_text(encoding="utf-8"))
    entities, aliases = normalize_nodes(raw.get("nodes", []))
    _write_csv(
        entities_path,
        entities,
        ["id", "external_id", "name", "canonical_name", "entity_type", "gender", "description", "notes"],
    )
    _write_csv(aliases_path, aliases, ["id", "entity_id", "alias", "language", "alias_type", "notes"])
    return entities, aliases


def main() -> None:
    parser = argparse.ArgumentParser(description="Normalize draw.io nodes into seed CSV files.")
    parser.add_argument("--input", default="data/parsed/drawio_raw.json")
    parser.add_argument("--entities-output", default="data/seed/entities.csv")
    parser.add_argument("--aliases-output", default="data/seed/aliases.csv")
    args = parser.parse_args()
    normalize_file(args.input, args.entities_output, args.aliases_output)


if __name__ == "__main__":
    main()
