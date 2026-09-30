# """
# Greedy Graph Burning algorithm based on closeness centrality.

# The algorithm selects, at each round, the unburned vertex with the
# highest raw closeness centrality in the residual graph induced by
# the currently unburned vertices.

# For disconnected residual graphs, distances are summed only over
# reachable vertices. Isolated vertices receive a score of 0.0.

# Tie-breaking is deterministic: vertices are ordered by str(vertex).
# """

# from __future__ import annotations

# import inspect
# from typing import Any, Hashable, Optional

# import networkx as nx

# from src.burning_simulation import BurningSimulator, BurningResult


# class GreedyClosenessAlgorithm:
#     """Adaptive greedy strategy based on residual closeness centrality."""

#     def __init__(self, graph: nx.Graph) -> None:
#         """
#         Initialize the algorithm.

#         Args:
#             graph: An undirected NetworkX graph.

#         Raises:
#             TypeError: If graph is not a NetworkX graph.
#             ValueError: If graph is directed or empty.
#         """
#         if not isinstance(graph, nx.Graph):
#             raise TypeError("graph must be a NetworkX graph.")

#         if graph.is_directed():
#             raise ValueError("Graph Burning requires an undirected graph.")

#         if graph.number_of_nodes() == 0:
#             raise ValueError("The graph must contain at least one vertex.")

#         self.graph = graph.copy()

#     @staticmethod
#     def _vertex_sort_key(vertex: Hashable) -> str:
#         """Return a deterministic key for tie-breaking."""
#         return str(vertex)

#     def _calculate_residual_closeness(
#         self,
#         residual_graph: nx.Graph,
#     ) -> dict[Hashable, float]:
#         """
#         Calculate raw closeness centrality on a residual graph.

#         For each vertex v:
#             closeness(v) = 1 / sum(distance(v, u))

#         Only reachable vertices are included in the distance sum.
#         Isolated vertices receive a score of 0.0.
#         """
#         scores: dict[Hashable, float] = {}

#         for vertex in residual_graph.nodes:
#             distances = nx.single_source_shortest_path_length(
#                 residual_graph,
#                 source=vertex,
#             )

#             distance_sum = sum(
#                 distance
#                 for target, distance in distances.items()
#                 if target != vertex
#             )

#             scores[vertex] = (
#                 1.0 / distance_sum
#                 if distance_sum > 0
#                 else 0.0
#             )

#         return scores

#     def select_source(
#         self,
#         unburned_vertices: set[Hashable],
#     ) -> Optional[Hashable]:
#         """
#         Select the unburned vertex with the highest residual closeness.

#         Args:
#             unburned_vertices: Vertices that have not yet burned.

#         Returns:
#             The selected vertex, or None if no candidate remains.
#         """
#         if not unburned_vertices:
#             return None

#         residual_graph = self.graph.subgraph(unburned_vertices).copy()
#         scores = self._calculate_residual_closeness(residual_graph)

#         return min(
#             scores,
#             key=lambda vertex: (
#                 -scores[vertex],
#                 self._vertex_sort_key(vertex),
#             ),
#         )

#     def _simulate(self, sources: list[Hashable]) -> BurningResult:
#         """
#         Run BurningSimulator with the source sequence.

#         The call adapts to the signature defined in
#         src/burning_simulation.py:
#             - BurningSimulator() or BurningSimulator(graph)
#             - simulate(sources) or simulate(graph, sources)
#               (or simulate(sources, graph))
#         """

#         def required_params(func) -> list[str]:
#             return [
#                 name
#                 for name, param in inspect.signature(func).parameters.items()
#                 if name != "self"
#                 and param.default is inspect.Parameter.empty
#                 and param.kind
#                 in (
#                     inspect.Parameter.POSITIONAL_ONLY,
#                     inspect.Parameter.POSITIONAL_OR_KEYWORD,
#                 )
#             ]

#         # Constructor: pass the graph only if it requires arguments.
#         if required_params(BurningSimulator.__init__):
#             simulator = BurningSimulator(self.graph)
#         else:
#             simulator = BurningSimulator()

#         # simulate(): decide what to send from the required parameters.
#         needed = required_params(simulator.simulate)

#         if len(needed) <= 1:
#             return simulator.simulate(sources)

#         args = []
#         for name in needed:
#             if "graph" in name:
#                 args.append(self.graph)
#             elif "source" in name or "sequence" in name:
#                 args.append(sources)
#             else:
#                 args.append(None)

#         # Names not recognised: default to (graph, sources).
#         if None in args:
#             args = [self.graph, sources]

#         return simulator.simulate(*args)

#     def run(self) -> BurningResult:
#         """
#         Execute the greedy closeness strategy.

#         At each round, the source is selected from the current
#         unburned vertices. The final source sequence is passed to
#         BurningSimulator to obtain the complete simulation result.
#         """
#         unburned = set(self.graph.nodes)
#         burned: set[Hashable] = set()
#         sources: list[Hashable] = []

#         while unburned:
#             source = self.select_source(unburned)

#             if source is None:
#                 break

#             sources.append(source)

#             # Spread from vertices burned before this round.
#             spread = {
#                 neighbor
#                 for vertex in burned
#                 for neighbor in self.graph.neighbors(vertex)
#                 if neighbor not in burned
#             }

#             burned.update(spread)
#             burned.add(source)
#             unburned = set(self.graph.nodes) - burned

#         return self._simulate(sources)


# def run_greedy_closeness(graph: nx.Graph) -> BurningResult:
#     """
#     Convenience function to execute the greedy closeness algorithm.

#     Args:
#         graph: An undirected NetworkX graph.

#     Returns:
#         The simulation result.
#     """
#     return GreedyClosenessAlgorithm(graph).run()

"""Stratégie gloutonne par centralité de proximité (énoncé du TP1)."""

from __future__ import annotations

import networkx as nx

from src.reference_burning import ReferenceBurningResult, burn_by_centrality_tp


class GreedyClosenessAlgorithm:
    """
    À chaque tour : propagation du feu, puis nouvelle source = sommet non
    brûlé de plus grande proximité C_C(i) = 1 / somme_j s_G(i, j).
    """

    def __init__(self, graph: nx.Graph) -> None:
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph must be a NetworkX graph.")

        if graph.is_directed():
            raise ValueError("Graph Burning requires an undirected graph.")

        if graph.number_of_nodes() == 0:
            raise ValueError("The graph must contain at least one vertex.")

        self.graph = graph.copy()

    def run(self) -> ReferenceBurningResult:
        return burn_by_centrality_tp(self.graph, "closeness")


def run_greedy_closeness(graph: nx.Graph) -> ReferenceBurningResult:
    """Convenience function to execute the closeness strategy."""
    return GreedyClosenessAlgorithm(graph).run()