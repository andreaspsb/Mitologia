import unittest

from scripts.normalize_relationships import normalize_edges


class NormalizeRelationshipsTests(unittest.TestCase):
    def test_maps_edges_to_relationships_with_known_type(self):
        raw = {
            "nodes": [
                {"id": "gaia", "label": "Gaia"},
                {"id": "urano", "label": "Urano"},
            ],
            "edges": [
                {"id": "edge-1", "source": "gaia", "target": "urano", "label": "mãe"},
            ],
        }

        relationships = normalize_edges(raw)

        self.assertEqual(
            relationships[0],
            {
                "id": "edge-1",
                "source_entity_id": "gaia",
                "target_entity_id": "urano",
                "relationship_type": "parent_of",
                "certainty": "traditional",
                "variant_group": "",
                "notes": "Original label: mãe",
                "source_id": "",
            },
        )

    def test_skips_edges_without_valid_entities(self):
        raw = {
            "nodes": [{"id": "gaia", "label": "Gaia"}],
            "edges": [{"id": "edge-1", "source": "gaia", "target": "missing", "label": ""}],
        }

        self.assertEqual(normalize_edges(raw), [])

    def test_defaults_unknown_or_empty_labels_without_arrow_to_associated_with(self):
        raw = {
            "nodes": [
                {"id": "zeus", "label": "Zeus/Júpiter"},
                {"id": "raio", "label": "Raio"},
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "zeus",
                    "target": "raio",
                    "label": "",
                    "style": "endArrow=none;dashed=1;",
                }
            ],
        }

        relationships = normalize_edges(raw)

        self.assertEqual(relationships[0]["relationship_type"], "associated_with")
        self.assertEqual(relationships[0]["notes"], "")

    def test_inferrs_parent_relationship_from_unlabeled_direct_arrow(self):
        raw = {
            "nodes": [
                {"id": "caos", "label": "Caos"},
                {"id": "gaia", "label": "Gaia"},
            ],
            "edges": [
                {
                    "id": "edge-1",
                    "source": "caos",
                    "target": "gaia",
                    "label": "",
                    "style": "endArrow=classic;html=1;rounded=0;",
                }
            ],
        }

        relationships = normalize_edges(raw)

        self.assertEqual(relationships[0]["relationship_type"], "parent_of")
        self.assertEqual(relationships[0]["notes"], "Inferred from direct arrow")

    def test_inferrs_parent_relationships_through_unlabeled_rhombus_connectors(self):
        raw = {
            "nodes": [
                {"id": "erebo", "label": "Érebo"},
                {"id": "nix", "label": "Nix"},
                {"id": "connector", "label": "", "style": "rhombus;whiteSpace=wrap;html=1;"},
                {"id": "eter", "label": "Éter"},
                {"id": "hemera", "label": "Hemera"},
            ],
            "edges": [
                {"id": "edge-1", "source": "erebo", "target": "connector", "label": ""},
                {"id": "edge-2", "source": "nix", "target": "connector", "label": ""},
                {"id": "edge-3", "source": "connector", "target": "eter", "label": ""},
                {"id": "edge-4", "source": "connector", "target": "hemera", "label": ""},
            ],
        }

        relationships = normalize_edges(raw)

        self.assertEqual(len(relationships), 4)
        self.assertEqual(relationships[0]["id"], "connector-edge-1-edge-3")
        self.assertEqual(relationships[0]["source_entity_id"], "erebo")
        self.assertEqual(relationships[0]["target_entity_id"], "eter")
        self.assertEqual(relationships[0]["relationship_type"], "parent_of")
        self.assertEqual(relationships[0]["notes"], "Inferred from rhombus connector: connector")


if __name__ == "__main__":
    unittest.main()
