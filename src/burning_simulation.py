
from __future__ import annotations

from dataclasses import dataclass
from typing import Hashable, Iterable

import networkx as nx


Vertex = Hashable


class BurningSimulationError(ValueError):
    """Raised when a burning simulation receives invalid input."""


@dataclass(frozen=True, slots=True)
class BurningRound:
    """Immutable snapshot of one burning round."""

    round_number: int
    source: Vertex
    spread_vertices: frozenset[Vertex]
    newly_burned: frozenset[Vertex]
    burned_vertices: frozenset[Vertex]
    unburned_vertices: frozenset[Vertex]


@dataclass(frozen=True, slots=True)
class BurningResult:
    """Complete result of a graph burning simulation."""

    source_sequence: tuple[Vertex, ...]
    rounds: tuple[BurningRound, ...]
    burned_vertices: frozenset[Vertex]
    unburned_vertices: frozenset[Vertex]
    total_vertices: int
    is_complete: bool

    @property
    def number_of_rounds(self) -> int:
        """Number of rounds actually simulated."""
        return len(self.rounds)

    @property
    def burned_count(self) -> int:
        """Number of vertices burned at the end."""
        return len(self.burned_vertices)

    @property
    def unburned_count(self) -> int:
        """Number of vertices still unburned."""
        return len(self.unburned_vertices)

    @property
    def burning_number_candidate(self) -> int | None:
        """
        Return the number of rounds if the graph is fully burned.

        This is not necessarily the optimal burning number.
        """
        if self.is_complete:
            return self.number_of_rounds
        return None


class BurningSimulator:
    """
    Simulate the Graph Burning process on an undirected graph.

    At each round:
        1. Select a source that was unburned at the start of the round.
        2. Spread fire from vertices burned before the current round.
        3. Add the source to the burned set.
        4. Store the complete round snapshot.

    The fire spreads at most one edge per round.
    """

    def simulate(
        self,
        graph: nx.Graph,
        sources: Iterable[Vertex],
    ) -> BurningResult:
        """Run a burning simulation using the supplied source sequence."""

        self._validate_graph(graph)

        source_sequence = tuple(sources)
        graph_vertices = set(graph.nodes)

        if not source_sequence and graph.number_of_nodes() > 0:
            raise BurningSimulationError(
                "The source sequence cannot be empty for a non-empty graph."
            )

        burned: set[Vertex] = set()
        history: list[BurningRound] = []

        for round_number, source in enumerate(
            source_sequence, start=1
        ):
            if source not in graph_vertices:
                raise BurningSimulationError(
                    f"Source {source!r} does not belong to the graph."
                )

            if source in burned:
                raise BurningSimulationError(
                    f"Source {source!r} is already burned before "
                    f"round {round_number}."
                )

            # Only vertices burned before this round spread the fire.
            previous_burned = set(burned)

            spread_vertices: set[Vertex] = set()

            for vertex in previous_burned:
                spread_vertices.update(graph.neighbors(vertex))

            # Do not count vertices that were already burned.
            spread_vertices.difference_update(previous_burned)

            # The source and the spreading fire ignite in the same round.
            newly_burned = spread_vertices | {source}

            burned.update(newly_burned)

            unburned = graph_vertices - burned

            history.append(
                BurningRound(
                    round_number=round_number,
                    source=source,
                    spread_vertices=frozenset(spread_vertices),
                    newly_burned=frozenset(newly_burned),
                    burned_vertices=frozenset(burned),
                    unburned_vertices=frozenset(unburned),
                )
            )

            # Stop early if the entire graph is burned.
            if not unburned:
                break

        unburned_vertices = graph_vertices - burned

        return BurningResult(
            source_sequence=tuple(
                round_state.source for round_state in history
            ),
            rounds=tuple(history),
            burned_vertices=frozenset(burned),
            unburned_vertices=frozenset(unburned_vertices),
            total_vertices=graph.number_of_nodes(),
            is_complete=not unburned_vertices,
        )

    @staticmethod
    def _validate_graph(graph: nx.Graph) -> None:
        """Validate the graph structure before simulation."""

        if not isinstance(graph, nx.Graph):
            raise BurningSimulationError(
                "The graph must be a NetworkX Graph."
            )

        if graph.is_directed():
            raise BurningSimulationError(
                "Graph Burning requires an undirected graph."
            )

        if graph.is_multigraph():
            raise BurningSimulationError(
                "MultiGraph is not supported."
            )

        if nx.number_of_selfloops(graph) > 0:
            raise BurningSimulationError(
                "The graph must not contain self-loops."
            )


def simulate(
    graph: nx.Graph,
    sources: Iterable[Vertex],
) -> BurningResult:
    """Convenience function for running a simulation."""

    return BurningSimulator().simulate(graph, sources)