
import networkx as nx
import pytest

from src.centrality import (
    CentralityCalculator,
    CentralityError,
    betweenness_centrality,
    closeness_centrality,
    degree_centrality,
)


@pytest.fixture
def calculator():
    return CentralityCalculator()


def test_degree_centrality_path_graph(calculator):
    graph = nx.path_graph(4)

    scores = calculator.degree_centrality(graph)

    assert scores == {
        0: 1.0,
        1: 2.0,
        2: 2.0,
        3: 1.0,
    }


def test_degree_centrality_star_graph(calculator):
    graph = nx.star_graph(3)

    scores = calculator.degree_centrality(graph)

    assert scores[0] == 3.0
    assert scores[1] == 1.0
    assert scores[2] == 1.0
    assert scores[3] == 1.0


def test_closeness_centrality_path_graph(calculator):
    graph = nx.path_graph(4)

    scores = calculator.closeness_centrality(graph)

    assert scores[0] == pytest.approx(1 / 6)
    assert scores[1] == pytest.approx(1 / 4)
    assert scores[2] == pytest.approx(1 / 4)
    assert scores[3] == pytest.approx(1 / 6)


def test_closeness_centrality_single_vertex(calculator):
    graph = nx.Graph()
    graph.add_node(0)

    scores = calculator.closeness_centrality(graph)

    assert scores == {0: 0.0}


def test_closeness_centrality_disconnected_graph(calculator):
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (2, 3)])

    with pytest.raises(CentralityError, match="connected graph"):
        calculator.closeness_centrality(graph)


def test_betweenness_centrality_path_graph(calculator):
    graph = nx.path_graph(4)

    scores = calculator.betweenness_centrality(graph)

    assert scores[0] == pytest.approx(0.0)
    assert scores[1] == pytest.approx(2.0)
    assert scores[2] == pytest.approx(2.0)
    assert scores[3] == pytest.approx(0.0)


def test_betweenness_centrality_star_graph(calculator):
    graph = nx.star_graph(3)

    scores = calculator.betweenness_centrality(graph)

    assert scores[0] == pytest.approx(3.0)
    assert scores[1] == pytest.approx(0.0)
    assert scores[2] == pytest.approx(0.0)
    assert scores[3] == pytest.approx(0.0)


def test_betweenness_centrality_triangle(calculator):
    graph = nx.complete_graph(3)

    scores = calculator.betweenness_centrality(graph)

    assert all(score == pytest.approx(0.0) for score in scores.values())


def test_calculate_all(calculator):
    graph = nx.path_graph(4)

    results = calculator.calculate_all(graph)

    assert set(results) == {
        "degree",
        "closeness",
        "betweenness",
    }

    assert len(results["degree"]) == 4
    assert len(results["closeness"]) == 4
    assert len(results["betweenness"]) == 4


def test_rank_vertices_descending(calculator):
    scores = {0: 1.0, 1: 3.0, 2: 2.0}

    ranked = calculator.rank_vertices(scores)

    assert ranked == [
        (1, 3.0),
        (2, 2.0),
        (0, 1.0),
    ]


def test_rank_vertices_ascending(calculator):
    scores = {0: 1.0, 1: 3.0, 2: 2.0}

    ranked = calculator.rank_vertices(
        scores,
        descending=False,
    )

    assert ranked == [
        (0, 1.0),
        (2, 2.0),
        (1, 3.0),
    ]


def test_empty_graph():
    graph = nx.Graph()

    assert degree_centrality(graph) == {}
    assert closeness_centrality(graph) == {}
    assert betweenness_centrality(graph) == {}


def test_betweenness_disconnected_graph(calculator):
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (2, 3)])

    scores = calculator.betweenness_centrality(graph)

    assert scores == {
        0: 0.0,
        1: 0.0,
        2: 0.0,
        3: 0.0,
    }


def test_directed_graph_is_rejected(calculator):
    graph = nx.DiGraph()
    graph.add_edge(0, 1)

    with pytest.raises(CentralityError, match="undirected"):
        calculator.degree_centrality(graph)


def test_self_loop_is_rejected(calculator):
    graph = nx.Graph()
    graph.add_edge(0, 0)

    with pytest.raises(CentralityError, match="self-loops"):
        calculator.degree_centrality(graph)