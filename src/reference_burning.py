"""
Algorithmes gloutons de Graph Burning basés sur la centralité.

Deux procédures sont disponibles :

1. burn_by_centrality (degré, notebook de référence)
   Centralité calculée une fois ; à chaque étape on brûle le sommet
   non brûlé le plus central ET tous ses voisins ; le résultat est le
   nombre d'étapes.

2. burn_by_centrality_tp (closeness et betweenness, énoncé du TP1)
   Processus de combustion de l'énoncé :
       - à chaque tour t, le feu se propage : tout sommet non brûlé
         voisin d'un sommet brûlé aux tours précédents brûle ;
       - puis on choisit une nouvelle source : le sommet encore non
         brûlé de plus grande centralité ;
       - le processus s'arrête quand tous les sommets sont brûlés ;
       - le burning number estimé est le nombre de tours.
   La centralité est calculée une seule fois sur le graphe complet
   (heuristique "maximum centralité", MECH). Égalités : premier
   sommet dans l'ordre de graph.nodes.

Mesures de l'énoncé (section 2) :
    degré         C_D(i) = somme des A_ij
    proximité     C_C(i) = 1 / somme_j s_G(i, j)
    intermédiarité C_B(i) = somme_{j != i != k} sigma_jk(i) / sigma_jk
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Hashable, Optional

import networkx as nx

Vertex = Hashable


# ----------------------------------------------------------------------
# Résultats
# ----------------------------------------------------------------------
@dataclass(frozen=True, slots=True)
class ReferenceRound:
    """Un tour du processus (source None si le tour n'a fait que propager)."""

    round_number: int
    source: Optional[Vertex]
    newly_burned: tuple[Vertex, ...]
    burned_vertices: tuple[Vertex, ...]  # cumulatif


@dataclass(frozen=True, slots=True)
class ReferenceBurningResult:
    """Résultat d'une exécution (mêmes attributs que ceux lus par l'interface)."""

    strategy: str
    total_vertices: int
    source_sequence: tuple[Vertex, ...]
    rounds: tuple[ReferenceRound, ...]

    @property
    def number_of_rounds(self) -> int:
        return len(self.rounds)

    @property
    def burning_number(self) -> int:
        """Nombre de tours (ou d'étapes pour la procédure de référence)."""
        return len(self.rounds)

    @property
    def burned_count(self) -> int:
        return len(self.rounds[-1].burned_vertices) if self.rounds else 0

    @property
    def unburned_count(self) -> int:
        return self.total_vertices - self.burned_count

    @property
    def is_complete(self) -> bool:
        return self.burned_count == self.total_vertices


def validate_graph(graph: nx.Graph) -> None:
    """Vérifie que le graphe est un graphe simple non orienté."""
    if not isinstance(graph, nx.Graph):
        raise TypeError("graph must be a NetworkX graph.")

    if graph.is_directed():
        raise ValueError("Graph Burning requires an undirected graph.")

    if graph.is_multigraph():
        raise ValueError("MultiGraph is not supported.")


def _best_unburned(
    graph: nx.Graph,
    burned: set[Vertex],
    scores: dict[Vertex, float],
) -> Vertex:
    """Sommet non brûlé de score maximal (premier dans graph.nodes si égalité)."""
    return max(
        (node for node in graph.nodes if node not in burned),
        key=lambda node: scores[node],
    )


# ----------------------------------------------------------------------
# 1. Procédure du notebook de référence (utilisée par le degré)
# ----------------------------------------------------------------------
CENTRALITIES: dict[str, Callable[[nx.Graph], dict]] = {
    "degree": nx.degree_centrality,
    "closeness": nx.closeness_centrality,
    "betweenness": nx.betweenness_centrality,
}


def burn_by_centrality(graph: nx.Graph, strategy: str) -> ReferenceBurningResult:
    """Brûle à chaque étape le sommet le plus central et ses voisins."""
    if strategy not in CENTRALITIES:
        supported = ", ".join(CENTRALITIES)
        raise ValueError(f"Unknown strategy '{strategy}'. Expected: {supported}")

    validate_graph(graph)

    centrality = CENTRALITIES[strategy](graph)

    burned: set[Vertex] = set()
    burned_order: list[Vertex] = []
    sources: list[Vertex] = []
    rounds: list[ReferenceRound] = []

    while len(burned) < len(graph):
        source = _best_unburned(graph, burned, centrality)

        newly_burned: list[Vertex] = []

        for vertex in (source, *graph.neighbors(source)):
            if vertex not in burned:
                burned.add(vertex)
                burned_order.append(vertex)
                newly_burned.append(vertex)

        sources.append(source)
        rounds.append(
            ReferenceRound(
                round_number=len(rounds) + 1,
                source=source,
                newly_burned=tuple(newly_burned),
                burned_vertices=tuple(burned_order),
            )
        )

    return ReferenceBurningResult(
        strategy=strategy,
        total_vertices=graph.number_of_nodes(),
        source_sequence=tuple(sources),
        rounds=tuple(rounds),
    )


# ----------------------------------------------------------------------
# 2. Procédure de l'énoncé du TP1 (closeness et betweenness)
# ----------------------------------------------------------------------
def closeness_tp(graph: nx.Graph) -> dict[Vertex, float]:
    """
    Centralité de proximité de l'énoncé : C_C(i) = 1 / somme_j s_G(i, j).

    Les distances infinies (graphe non connexe) sont ignorées : la somme
    porte sur les sommets atteignables. Un sommet isolé a un score de 0.
    """
    scores: dict[Vertex, float] = {}

    for vertex in graph.nodes:
        distances = nx.single_source_shortest_path_length(graph, vertex)
        total = sum(d for target, d in distances.items() if target != vertex)
        scores[vertex] = 1.0 / total if total > 0 else 0.0

    return scores


def betweenness_tp(graph: nx.Graph) -> dict[Vertex, float]:
    """
    Centralité d'intermédiarité de l'énoncé :
    C_B(i) = somme sigma_jk(i) / sigma_jk.

    Non normalisée. Dans un graphe non orienté, chaque paire {j, k} est
    comptée une fois (le classement des sommets est identique à celui
    d'une somme sur les paires ordonnées).
    """
    return nx.betweenness_centrality(graph, normalized=False, endpoints=False)


TP_MEASURES: dict[str, Callable[[nx.Graph], dict[Vertex, float]]] = {
    "degree": lambda g: {v: float(d) for v, d in g.degree()},
    "closeness": closeness_tp,
    "betweenness": betweenness_tp,
}


def burn_by_centrality_tp(graph: nx.Graph, strategy: str) -> ReferenceBurningResult:
    """
    Graph Burning glouton selon la définition de l'énoncé du TP1.

    Args:
        graph: graphe NetworkX non orienté.
        strategy: "degree", "closeness" ou "betweenness".
    """
    if strategy not in TP_MEASURES:
        supported = ", ".join(TP_MEASURES)
        raise ValueError(f"Unknown strategy '{strategy}'. Expected: {supported}")

    validate_graph(graph)

    scores = TP_MEASURES[strategy](graph)

    burned: set[Vertex] = set()
    burned_order: list[Vertex] = []
    sources: list[Vertex] = []
    rounds: list[ReferenceRound] = []

    # Sommets brûlés au tour précédent : seuls eux peuvent encore
    # propager le feu à de nouveaux sommets.
    frontier: list[Vertex] = []

    while len(burned) < len(graph):
        newly_burned: list[Vertex] = []

        # 1. Propagation : voisins non brûlés des sommets déjà brûlés.
        for vertex in frontier:
            for neighbor in graph.neighbors(vertex):
                if neighbor not in burned:
                    burned.add(neighbor)
                    burned_order.append(neighbor)
                    newly_burned.append(neighbor)

        # 2. Nouvelle source : sommet non brûlé le plus central.
        source: Optional[Vertex] = None

        if len(burned) < len(graph):
            source = _best_unburned(graph, burned, scores)
            burned.add(source)
            burned_order.append(source)
            newly_burned.append(source)
            sources.append(source)

        rounds.append(
            ReferenceRound(
                round_number=len(rounds) + 1,
                source=source,
                newly_burned=tuple(newly_burned),
                burned_vertices=tuple(burned_order),
            )
        )

        frontier = newly_burned

    return ReferenceBurningResult(
        strategy=strategy,
        total_vertices=graph.number_of_nodes(),
        source_sequence=tuple(sources),
        rounds=tuple(rounds),
    )