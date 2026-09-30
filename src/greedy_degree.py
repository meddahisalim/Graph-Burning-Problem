
# from __future__ import annotations

# from typing import Hashable

# import networkx as nx

# from src.burning_simulation import (
#     BurningResult,
#     BurningSimulationError,
#     BurningSimulator,
# )


# Vertex = Hashable


# class GreedyDegreeError(ValueError):
#     """Raised when the greedy degree algorithm receives invalid input."""


# class GreedyDegreeAlgorithm:
#     """
#     Greedy Graph Burning algorithm based on residual degree.

#     At each round:
#         1. Determine the currently unburned vertices.
#         2. Compute each unburned vertex's degree inside the
#            subgraph induced by unburned vertices.
#         3. Select the vertex with maximum residual degree.
#         4. Spread the fire according to the burning rules.

#     Ties are resolved deterministically using str(vertex).
#     """

#     def __init__(self) -> None:
#         self._simulator = BurningSimulator()

#     def run(self, graph: nx.Graph) -> BurningResult:
#         """
#         Execute the greedy degree algorithm.

#         Returns:
#             BurningResult containing the selected source sequence
#             and the full simulation history.
#         """

#         self._validate_graph(graph)

#         if graph.number_of_nodes() == 0:
#             return self._simulator.simulate(graph, [])

#         graph_vertices = set(graph.nodes)
#         burned: set[Vertex] = set()
#         sources: list[Vertex] = []

#         while burned != graph_vertices:
#             unburned = graph_vertices - burned

#             source = self.select_source(
#                 graph=graph,
#                 unburned_vertices=unburned,
#             )

#             sources.append(source)

#             # Only vertices burned before this round spread fire.
#             spread_vertices: set[Vertex] = set()

#             for vertex in burned:
#                 spread_vertices.update(graph.neighbors(vertex))

#             spread_vertices.difference_update(burned)

#             # Ignite the new source and all vertices reached
#             # by the previous fire front.
#             burned.update(spread_vertices)
#             burned.add(source)

#         return self._simulator.simulate(graph, sources)

#     def select_source(
#         self,
#         graph: nx.Graph,
#         unburned_vertices: set[Vertex] | frozenset[Vertex],
#     ) -> Vertex:
#         """
#         Select the unburned vertex with the highest residual degree.

#         Residual degree is computed only among unburned vertices.
#         """

#         self._validate_graph(graph)

#         unburned = set(unburned_vertices)

#         if not unburned:
#             raise GreedyDegreeError(
#                 "Cannot select a source: no unburned vertices remain."
#             )

#         graph_vertices = set(graph.nodes)

#         unknown_vertices = unburned - graph_vertices

#         if unknown_vertices:
#             raise GreedyDegreeError(
#                 f"Unknown vertices in unburned set: {unknown_vertices!r}"
#             )

#         residual_degrees = self._get_residual_degrees(
#             graph,
#             unburned,
#         )

#         return min(
#             residual_degrees,
#             key=lambda vertex: (
#                 -residual_degrees[vertex],
#                 str(vertex),
#             ),
#         )

#     @staticmethod
#     def _get_residual_degrees(
#         graph: nx.Graph,
#         unburned_vertices: set[Vertex],
#     ) -> dict[Vertex, int]:
#         """
#         Compute degrees in the subgraph induced by unburned vertices.
#         """

#         residual_graph = graph.subgraph(unburned_vertices)

#         return dict(residual_graph.degree())

#     @staticmethod
#     def _validate_graph(graph: nx.Graph) -> None:
#         """Validate graph structure."""

#         if not isinstance(graph, nx.Graph):
#             raise GreedyDegreeError(
#                 "The graph must be a NetworkX Graph."
#             )

#         if graph.is_directed():
#             raise GreedyDegreeError(
#                 "The graph must be undirected."
#             )

#         if graph.is_multigraph():
#             raise GreedyDegreeError(
#                 "MultiGraph is not supported."
#             )

#         if nx.number_of_selfloops(graph) > 0:
#             raise GreedyDegreeError(
#                 "The graph must not contain self-loops."
#             )


# def run_greedy_degree(graph: nx.Graph) -> BurningResult:
#     """Convenience function for running the greedy degree algorithm."""

#     return GreedyDegreeAlgorithm().run(graph)

"""Stratégie par centralité de degré (algorithme de référence)."""

from __future__ import annotations

import networkx as nx

from src.reference_burning import ReferenceBurningResult, burn_by_centrality


class GreedyDegreeError(ValueError):
    """Raised when the greedy degree algorithm receives invalid input."""


class GreedyDegreeAlgorithm:
    """Brûle à chaque étape le sommet non brûlé de plus grand degré."""

    def run(self, graph: nx.Graph) -> ReferenceBurningResult:
        self._validate_graph(graph)
        return burn_by_centrality(graph, "degree")

    @staticmethod
    def _validate_graph(graph: nx.Graph) -> None:
        if not isinstance(graph, nx.Graph):
            raise GreedyDegreeError("The graph must be a NetworkX Graph.")

        if graph.is_directed():
            raise GreedyDegreeError("The graph must be undirected.")

        if graph.is_multigraph():
            raise GreedyDegreeError("MultiGraph is not supported.")


def run_greedy_degree(graph: nx.Graph) -> ReferenceBurningResult:
    """Convenience function for running the degree strategy."""
    return GreedyDegreeAlgorithm().run(graph)