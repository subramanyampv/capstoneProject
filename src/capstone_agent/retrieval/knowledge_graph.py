"""Small provenance graph over synthetic fixture metadata; no inferred policy authority."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, node_id, kind, label):
        self.nodes[node_id] = {"id": node_id, "kind": kind, "label": label}

    def add_edge(self, source, relation, target, *, source_id, version):
        if source not in self.nodes or target not in self.nodes or not source_id or not version:
            raise ValueError("Graph edges require existing nodes and source/version provenance.")
        self.edges.append({"source": source, "relation": relation, "target": target,
                           "source_id": source_id, "version": version})

    @classmethod
    def from_fixtures(cls, root=ROOT):
        graph = cls()
        catalog = json.loads((root / "data/product_catalog.json").read_text())
        for product in catalog["products"]:
            category = "category:" + product["category"]
            graph.add_node(category, "category", product["category"])
            graph.add_node(product["sku"], "product", product["name"])
            graph.add_edge(product["sku"], "belongs_to", category,
                           source_id="data/product_catalog.json", version=catalog["version"])
        # Deliberately omit order/customer identities until authorization is integrated.
        graph.add_node("catalog", "document", "Product catalog")
        for product in catalog["products"]:
            graph.add_edge("catalog", "describes", product["sku"],
                           source_id="data/product_catalog.json", version=catalog["version"])
        return graph

    def neighborhood(self, node_id, *, max_hops=2):
        if not 0 <= max_hops <= 3:
            raise ValueError("Traversal budget is 0–3 hops.")
        if node_id not in self.nodes:
            return {"nodes": [], "edges": []}
        seen = {node_id}
        edges = []
        frontier = {node_id}
        for _ in range(max_hops):
            next_frontier = set()
            for edge in self.edges:
                if edge["source"] in frontier:
                    if edge not in edges:
                        edges.append(edge)
                    next_frontier.add(edge["target"])
            frontier = next_frontier - seen
            seen |= next_frontier
        return {"nodes": [self.nodes[key] for key in sorted(seen)], "edges": edges}

    def as_dict(self):
        return {"version": "kg-v1", "nodes": list(self.nodes.values()), "edges": self.edges,
                "limits": "Catalog metadata only; policy-section/version links await corpus ingestion. "
                          "Order data requires authorization. Graph relationships never grant permissions."}
