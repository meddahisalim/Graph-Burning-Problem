"""
Graph Burning strategy comparison and CSV export.

Compares:
- Greedy Degree
- Greedy Closeness
- Greedy Betweenness
- Greedy Improvement
"""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from pathlib import Path
from time import perf_counter
from typing import Any, Callable

import networkx as nx

from src.burning_simulation import BurningResult
from src.greedy_degree import run_greedy_degree
from src.greedy_closeness import run_greedy_closeness
from src.greedy_betweenness import run_greedy_betweenness
from src.improvements import run_best_greedy


@dataclass(frozen=True, slots=True)
class StrategyResult:
    """Metrics produced by one strategy on one graph."""

    graph_name: str
    strategy_name: str
    number_of_vertices: int
    number_of_edges: int
    number_of_rounds: int
    burned_count: int
    unburned_count: int
    is_complete: bool
    source_sequence: str
    execution_time_seconds: float


@dataclass(frozen=True, slots=True)
class GraphComparison:
    """Comparison results for a single graph."""

    graph_name: str
    results: tuple[StrategyResult, ...]

    @property
    def best_complete_result(self) -> StrategyResult | None:
        """Return the complete result with the fewest rounds."""
        complete = [
            result for result in self.results
            if result.is_complete
        ]

        if not complete:
            return None

        return min(
            complete,
            key=lambda result: (
                result.number_of_rounds,
                result.execution_time_seconds,
                result.strategy_name,
            ),
        )


class GraphComparisonRunner:
    """Run and compare Graph Burning strategies."""

    def __init__(self) -> None:
        self._strategies: dict[
            str, Callable[[nx.Graph], BurningResult]
        ] = {
            "greedy_degree": run_greedy_degree,
            "greedy_closeness": run_greedy_closeness,
            "greedy_betweenness": run_greedy_betweenness,
        }

    @staticmethod
    def _normalize_inputs(
        graph_name: Any,
        graph: Any,
    ) -> tuple[str, nx.Graph]:
        """
        Validate and normalize the inputs of compare_graph().

        Tolerates the two most common calling mistakes:
        - arguments swapped: compare_graph(graph, name);
        - a name that is not a string (converted with str()).
        """
        # Arguments given in the wrong order.
        if (
            isinstance(graph_name, nx.Graph)
            and not isinstance(graph, nx.Graph)
        ):
            graph_name, graph = graph, graph_name

        if not isinstance(graph, nx.Graph):
            raise TypeError(
                "graph must be a NetworkX graph "
                f"(received {type(graph).__name__})."
            )

        if graph.is_directed():
            raise ValueError("Graph Burning requires an undirected graph.")

        if graph.number_of_nodes() == 0:
            raise ValueError("The graph must contain at least one vertex.")

        name = str(graph_name) if graph_name else "Graphe"

        return name, graph

    def compare_graph(
        self,
        graph_name: str,
        graph: nx.Graph,
    ) -> GraphComparison:
        """Execute all strategies on one graph."""
        graph_name, graph = self._normalize_inputs(graph_name, graph)

        results: list[StrategyResult] = []

        for strategy_name, strategy in self._strategies.items():
            graph_copy = graph.copy()

            start = perf_counter()

            try:
                result = strategy(graph_copy)
            except Exception as exc:
                raise RuntimeError(
                    f"La stratégie '{strategy_name}' a échoué : {exc}"
                ) from exc

            elapsed = perf_counter() - start

            results.append(
                self._build_result(
                    graph_name=graph_name,
                    strategy_name=strategy_name,
                    graph=graph,
                    result=result,
                    elapsed=elapsed,
                )
            )

        # The improvement strategy compares the three greedy methods.
        start = perf_counter()

        try:
            improvement = run_best_greedy(graph.copy())
        except Exception as exc:
            raise RuntimeError(
                f"La stratégie 'greedy_improvement' a échoué : {exc}"
            ) from exc

        elapsed = perf_counter() - start

        results.append(
            self._build_result(
                graph_name=graph_name,
                strategy_name="greedy_improvement",
                graph=graph,
                result=improvement.best_result,
                elapsed=elapsed,
            )
        )

        return GraphComparison(
            graph_name=graph_name,
            results=tuple(results),
        )

    @staticmethod
    def _build_result(
        graph_name: str,
        strategy_name: str,
        graph: nx.Graph,
        result: BurningResult,
        elapsed: float,
    ) -> StrategyResult:
        """Convert a simulation result into comparison metrics."""
        return StrategyResult(
            graph_name=graph_name,
            strategy_name=strategy_name,
            number_of_vertices=graph.number_of_nodes(),
            number_of_edges=graph.number_of_edges(),
            number_of_rounds=result.number_of_rounds,
            burned_count=result.burned_count,
            unburned_count=result.unburned_count,
            is_complete=result.is_complete,
            source_sequence=repr(result.source_sequence),
            execution_time_seconds=round(elapsed, 8),
        )

    def compare_graphs(
        self,
        graphs: dict[str, nx.Graph],
    ) -> list[GraphComparison]:
        """Compare strategies on multiple named graphs."""
        return [
            self.compare_graph(name, graph)
            for name, graph in graphs.items()
        ]


def export_comparison_csv(
    comparisons: list[GraphComparison],
    output_path: str | Path,
) -> Path:
    """Export comparison results to a CSV file."""
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "graph_name",
        "strategy_name",
        "number_of_vertices",
        "number_of_edges",
        "number_of_rounds",
        "burned_count",
        "unburned_count",
        "is_complete",
        "source_sequence",
        "execution_time_seconds",
    ]

    with destination.open(
        mode="w",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            delimiter=";",
        )
        writer.writeheader()

        for comparison in comparisons:
            for result in comparison.results:
                writer.writerow(asdict(result))

    return destination