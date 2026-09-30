"""Stratégie gloutonne par centralité d'intermédiarité (énoncé du TP1)."""

from __future__ import annotations

import networkx as nx

from src.reference_burning import ReferenceBurningResult, burn_by_centrality_tp


class GreedyBetweennessAlgorithm:
    """
    À chaque tour : propagation du feu, puis nouvelle source = sommet non
    brûlé de plus grande intermédiarité C_B(i) = somme sigma_jk(i) / sigma_jk.
    """

    def __init__(self, graph: nx.Graph) -> None:
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph must be a NetworkX graph.")

        if graph.is_directed():
            raise ValueError("Graph Burning requires an undirected graph.")

        if graph.is_multigraph():
            raise ValueError("MultiGraph is not supported.")

        if graph.number_of_nodes() == 0:
            raise ValueError("The graph must contain at least one vertex.")

        self.graph = graph.copy()

    def run(self) -> ReferenceBurningResult:
        return burn_by_centrality_tp(self.graph, "betweenness")


def run_greedy_betweenness(graph: nx.Graph) -> ReferenceBurningResult:
    """Convenience function to execute the betweenness strategy."""
    return GreedyBetweennessAlgorithm(graph).run()