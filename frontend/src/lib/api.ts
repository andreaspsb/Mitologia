export type Alias = {
  id: string;
  entity_id: string;
  alias: string;
  language?: string | null;
  alias_type?: string | null;
  notes?: string | null;
};

export type Entity = {
  id: string;
  external_id?: string | null;
  name: string;
  canonical_name?: string | null;
  greek_name?: string | null;
  roman_name?: string | null;
  entity_type: string;
  gender?: string | null;
  description?: string | null;
  notes?: string | null;
  aliases: Alias[];
};

export type Relationship = {
  id: string;
  source_entity_id: string;
  source_name?: string | null;
  target_entity_id: string;
  target_name?: string | null;
  relationship_type: string;
  certainty: string;
  variant_group?: string | null;
  notes?: string | null;
  source_id?: string | null;
};

export type AuditSummary = {
  totals: {
    entities: number;
    relationships: number;
    unknown_entities: number;
    associated_relationships: number;
  };
  entity_type_counts: Record<string, number>;
  relationship_type_counts: Record<string, number>;
  unknown_entities: Array<{
    id: string;
    name: string;
    entity_type: string;
  }>;
  associated_relationships: Array<{
    id: string;
    source_entity_id: string;
    source_name: string;
    target_entity_id: string;
    target_name: string;
    relationship_type: string;
    notes?: string | null;
  }>;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function apiGet<T>(path: string): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    next: { revalidate: 60 },
  });
  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }
  return response.json() as Promise<T>;
}

export function getEntities(entityType?: string, limit = 100): Promise<Entity[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (entityType) {
    params.set("entity_type", entityType);
  }
  return apiGet<Entity[]>(`/entities?${params.toString()}`);
}

export function getEntity(id: string): Promise<Entity> {
  return apiGet<Entity>(`/entities/${id}`);
}

export function getEntityRelationships(id: string): Promise<Relationship[]> {
  return apiGet<Relationship[]>(`/entities/${id}/relationships`);
}

export function getRelationships(relationshipType?: string, limit = 100): Promise<Relationship[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (relationshipType) {
    params.set("relationship_type", relationshipType);
  }
  return apiGet<Relationship[]>(`/relationships?${params.toString()}`);
}

export function getAuditSummary(): Promise<AuditSummary> {
  return apiGet<AuditSummary>("/audit/summary");
}

export function searchEntities(query: string): Promise<Entity[]> {
  const params = new URLSearchParams({ q: query });
  return apiGet<Entity[]>(`/search?${params.toString()}`);
}
