import unittest

from scripts.normalize_entities import infer_entity_type, normalize_node_label, normalize_nodes


class NormalizeEntitiesTests(unittest.TestCase):
    def test_splits_aliases_and_preserves_external_id(self):
        nodes = [
            {
                "id": "zeus",
                "label": " Zeus / Júpiter ",
                "style": "rounded=1;",
            }
        ]

        entities, aliases = normalize_nodes(nodes)

        self.assertEqual(entities[0]["id"], "zeus")
        self.assertEqual(entities[0]["external_id"], "zeus")
        self.assertEqual(entities[0]["name"], "Zeus")
        self.assertEqual(aliases[0]["entity_id"], "zeus")
        self.assertEqual(aliases[0]["alias"], "Júpiter")
        self.assertEqual(aliases[0]["alias_type"], "roman")

    def test_cleans_html_and_duplicate_spaces(self):
        self.assertEqual(normalize_node_label("<b>Heracles</b>  /  Hercules"), "Heracles / Hercules")
        self.assertEqual(normalize_node_label("Abas<br>Rei de Argos"), "Abas Rei de Argos")

    def test_infers_entity_type_from_label(self):
        cases = {
            "Abas Rei de Argos 1384 - 1360": "king",
            "Mênfis Náiade": "nymph",
            "Titanomaquia": "event",
            "Leão de Nemeia": "monster",
            "Tártaro Submundo": "place",
            "Cinto de Hipólita": "object",
            "Gigantes": "group",
            "Zeus/Júpiter": "olympian",
        }

        for label, expected_type in cases.items():
            with self.subTest(label=label):
                self.assertEqual(infer_entity_type(label), expected_type)


if __name__ == "__main__":
    unittest.main()
