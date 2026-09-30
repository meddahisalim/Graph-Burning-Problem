
"""
Improvement module for Graph Burning.

This module compares the results of three greedy strategies:
- Degree centrality
- Closeness centrality
- Betweenness centrality

It selects the best complete result with the smallest number of rounds.

If no strategy burns the entire graph, it selects the result that burns
the largest number of vertices, then prefers fewer rounds.

This is a heuristic comparison, not an exact optimization algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

import networkx as nx

from src.burning_simulation import BurningResult
from src.greedy_degree import run_greedy_degree
from src.greedy_closeness import run_greedy_closeness
from src.greedy_betweenness import run_greedy_betweenness


class ImprovementError(ValueError):
    """Raised when the improvement procedure receives invalid input."""


@dataclass(frozen=True, slots=True)
class ImprovementResult:
    """Result of comparing greedy strategies."""

    best_strategy: str
    best_result: BurningResult
    all_results: dict[str, BurningResult]

    @property
    def best_rounds(self) -> int:
        """Number of rounds in the selected result."""
        return self.best_result.number_of_rounds

    @property
    def is_complete(self) -> bool:
        """Whether the selected result burns the entire graph."""
        return self.best_result.is_complete


class GreedyImprovement:
    """Compare greedy strategies and select the best result."""

    def __init__(self, graph: nx.Graph) -> None:
        """
        Initialize the comparison procedure.

        Args:
            graph: An undirected graph.

        Raises:
            TypeError: If graph is not a NetworkX graph.
            ValueError: If graph is directed or empty.
        """
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph must be a NetworkX graph.")

        if graph.is_directed():
            raise ValueError("Graph Burning requires an undirected graph.")

        if graph.number_of_nodes() == 0:
            raise ValueError("The graph must contain at least one vertex.")

        self.graph = graph.copy()

        self._strategies: dict[
            str, Callable[[nx.Graph], BurningResult]
        ] = {
            "degree": run_greedy_degree,
            "closeness": run_greedy_closeness,
            "betweenness": run_greedy_betweenness,
        }

    @staticmethod
    def _result_key(
        item: tuple[str, BurningResult],
    ) -> tuple[int, int, int]:
        """
        Ranking key for comparing strategy results.

        Priority:
        1. Complete results over incomplete results.
        2. Fewer rounds for complete results.
        3. More burned vertices for incomplete results.
        4. Fewer rounds when burned counts are equal.
        """
        _, result = item

        if result.is_complete:
            return (0, result.number_of_rounds, 0)

        return (
            1,
            -result.burned_count,
            result.number_of_rounds,
        )

    def run(self) -> ImprovementResult:
        """Execute all strategies and select the best result."""
        all_results: dict[str, BurningResult] = {}

        for strategy_name, strategy in self._strategies.items():
            all_results[strategy_name] = strategy(self.graph.copy())

        best_strategy, best_result = min(
            all_results.items(),
            key=self._result_key,
        )

        return ImprovementResult(
            best_strategy=best_strategy,
            best_result=best_result,
            all_results=all_results,
        )


def run_best_greedy(graph: nx.Graph) -> ImprovementResult:
    """Convenience function to compare the three greedy strategies."""
    return GreedyImprovement(graph).run()