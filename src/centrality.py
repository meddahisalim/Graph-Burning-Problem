
from __future__ import annotations

from collections.abc import Mapping
from typing import Hashable

import networkx as nx


Vertex = Hashable


class CentralityError(ValueError):
    """Raised when a centrality measure cannot be computed."""


class CentralityCalculator:
    """
    Calculate graph centrality measures.

    Supported measures:
        - Degree centrality: raw vertex degree
        - Closeness centrality: 1 / sum of shortest-path distances
        - Betweenness centrality: unnormalized shortest-path
          betweenness for unordered vertex pairs
    """

    @staticmethod
    def _validate_graph(graph: nx.Graph) -> None:
        """Validate the graph type."""

        if not isinstance(graph, nx.Graph):
            raise CentralityError(
                "The graph must be a NetworkX Graph."
            )

        if graph.is_directed():
            raise CentralityError(
                "Centrality calculations require an undirected graph."
            )

        if graph.is_multigraph():
            raise CentralityError(
                "MultiGraph is not supported."
            )

        if nx.number_of_selfloops(graph) > 0:
            raise CentralityError(
                "The graph must not contain self-loops."
            )

    def degree_centrality(
        self,
        graph: nx.Graph,
    ) -> dict[Vertex, float]:
        """
        Compute raw degree centrality.

        CD(v) = degree(v) = sum_j A[v, j]
        """

        self._validate_graph(graph)

        return {
            vertex: float(degree)
            for vertex, degree in graph.degree()
        }

    def closeness_centrality(
        self,
        graph: nx.Graph,
    ) -> dict[Vertex, float]:
        """
        Compute the course's unnormalized closeness formula.

        CC(v) = 1 / sum_{u != v} d(v, u)

        The graph must be connected unless it contains
        zero or one vertex.
        """

        self._validate_graph(graph)

        if graph.number_of_nodes() == 0:
            return {}

        if not nx.is_connected(graph):
            raise CentralityError(
                "Closeness centrality using the course formula "
                "requires a connected graph."
            )

        result: dict[Vertex, float] = {}

        for vertex in graph.nodes:
            distances = nx.single_source_shortest_path_length(
                graph, vertex
            )

            distance_sum = sum(
                distance
                for other, distance in distances.items()
                if other != vertex
            )

            if distance_sum == 0:
                # A graph with one vertex has no other vertices.
                result[vertex] = 0.0
            else:
                result[vertex] = 1.0 / distance_sum

        return result

    def betweenness_centrality(
        self,
        graph: nx.Graph,
    ) -> dict[Vertex, float]:
        """
        Compute unnormalized betweenness centrality.

        CB(v) = sum over unordered pairs {s, t}, s != t != v,
                of sigma_st(v) / sigma_st.

        For disconnected graphs, only pairs connected by a path
        contribute.
        """

        self._validate_graph(graph)

        if graph.number_of_nodes() == 0:
            return {}

        return nx.betweenness_centrality(
            graph,
            normalized=False,
            endpoints=False,
            weight=None,
        )

    def calculate_all(
        self,
        graph: nx.Graph,
    ) -> dict[str, dict[Vertex, float]]:
        """Calculate all three centrality measures."""

        return {
            "degree": self.degree_centrality(graph),
            "closeness": self.closeness_centrality(graph),
            "betweenness": self.betweenness_centrality(graph),
        }

    @staticmethod
    def rank_vertices(
        scores: Mapping[Vertex, float],
        descending: bool = True,
    ) -> list[tuple[Vertex, float]]:
        """
        Rank vertices by score.

        Ties are resolved by the string representation of the vertex,
        to provide deterministic output for comparable inputs.
        """

        return sorted(
            scores.items(),
            key=lambda item: (
                -item[1] if descending else item[1],
                str(item[0]),
            ),
        )


def degree_centrality(
    graph: nx.Graph,
) -> dict[Vertex, float]:
    return CentralityCalculator().degree_centrality(graph)


def closeness_centrality(
    graph: nx.Graph,
) -> dict[Vertex, float]:
    return CentralityCalculator().closeness_centrality(graph)


def betweenness_centrality(
    graph: nx.Graph,
) -> dict[Vertex, float]:
    return CentralityCalculator().betweenness_centrality(graph)


def calculate_all(
    graph: nx.Graph,
) -> dict[str, dict[Vertex, float]]:
    return CentralityCalculator().calculate_all(graph)