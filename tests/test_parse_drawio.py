import tempfile
import unittest
from pathlib import Path

from scripts.parse_drawio import parse_drawio_file
from scripts.parse_drawio import clean_label


class ParseDrawioTests(unittest.TestCase):
    def test_clean_label_keeps_word_boundaries_for_html_tags(self):
        self.assertEqual(clean_label("Abas<br>Rei de Argos"), "Abas Rei de Argos")

    def test_extracts_vertices_edges_labels_and_geometry(self):
        drawio = """<?xml version="1.0" encoding="UTF-8"?>
<mxfile>
  <diagram id="page-1" name="Page 1">
    <mxGraphModel>
      <root>
        <mxCell id="0" />
        <mxCell id="1" parent="0" />
        <mxCell id="zeus" value="Zeus/&lt;b&gt;Jupiter&lt;/b&gt;" style="rounded=1;" vertex="1" parent="1">
          <mxGeometry x="10" y="20" width="120" height="40" as="geometry" />
        </mxCell>
        <mxCell id="hera" value="Hera" style="ellipse;" vertex="1" parent="1" />
        <mxCell id="marriage" value="spouse" edge="1" parent="1" source="zeus" target="hera">
          <mxGeometry relative="1" as="geometry" />
        </mxCell>
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "sample.drawio"
            source.write_text(drawio, encoding="utf-8")

            result = parse_drawio_file(source)

        self.assertEqual(result["source_file"], str(source))
        self.assertEqual(result["pages"][0]["name"], "Page 1")
        self.assertEqual(len(result["nodes"]), 2)
        self.assertEqual(len(result["edges"]), 1)
        self.assertEqual(result["nodes"][0]["label"], "Zeus/Jupiter")
        self.assertEqual(result["nodes"][0]["geometry"]["x"], 10.0)
        self.assertEqual(result["edges"][0]["source"], "zeus")
        self.assertEqual(result["edges"][0]["target"], "hera")


if __name__ == "__main__":
    unittest.main()
