"use client";

import cytoscape from "cytoscape";
import { useEffect, useRef } from "react";
import type { Entity, Relationship } from "@/lib/api";

type GraphViewProps = {
  entities: Entity[];
  relationships: Relationship[];
};

export function GraphView({ entities, relationships }: GraphViewProps) {
  const containerRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }

    const graph = cytoscape({
      container: containerRef.current,
      elements: [
        ...entities.map((entity) => ({
          data: { id: entity.id, label: entity.name, type: entity.entity_type },
        })),
        ...relationships.map((relationship) => ({
          data: {
            id: relationship.id,
            source: relationship.source_entity_id,
            target: relationship.target_entity_id,
            label: relationship.relationship_type,
          },
        })),
      ],
      layout: { name: "cose", animate: false, fit: true, padding: 40 },
      style: [
        {
          selector: "node",
          style: {
            "background-color": "#285f74",
            color: "#1f2523",
            label: "data(label)",
            "font-size": 11,
            "text-valign": "bottom",
            "text-margin-y": 8,
          },
        },
        {
          selector: "edge",
          style: {
            "curve-style": "bezier",
            "line-color": "#9c8f78",
            "target-arrow-color": "#9c8f78",
            "target-arrow-shape": "triangle",
            width: 1.4,
          },
        },
      ],
    });

    return () => {
      graph.destroy();
    };
  }, [entities, relationships]);

  if (!entities.length) {
    return (
      <div className="graph-surface empty">
        <p>Nenhuma entidade encontrada para os filtros atuais.</p>
      </div>
    );
  }

  return <div className="graph-surface" ref={containerRef} />;
}
