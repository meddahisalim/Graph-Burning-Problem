
import networkx as nx
import pytest

from src.burning_simulation import (
    BurningSimulationError,
    BurningSimulator,
    simulate,
)


@pytest.fixture
def simulator():
    return BurningSimulator()


def test_single_vertex_graph():
    graph = nx.Graph()
    graph.add_node(0)

    result = simulate(graph, [0])

    assert result.is_complete
    assert result.number_of_rounds == 1
    assert result.burned_vertices == frozenset({0})
    assert result.unburned_vertices == frozenset()


def test_path_graph_propagation():
    graph = nx.path_graph(4)

    result = simulate(graph, [0, 3])

    assert result.is_complete
    assert result.number_of_rounds == 3

    assert result.rounds[0].burned_vertices == frozenset({0})
    assert result.rounds[1].burned_vertices == frozenset({0, 1, 3})
    assert result.rounds[2].burned_vertices == frozenset({0, 1, 2, 3})


def test_fire_spreads_only_one_edge_per_round():
    graph = nx.path_graph(5)

    result = simulate(graph, [0, 4])

    assert result.rounds[0].burned_vertices == frozenset({0})
    assert result.rounds[1].burned_vertices == frozenset({0, 1, 4})
    assert result.rounds[2].burned_vertices == frozenset({0, 1, 2, 3, 4})
    assert result.is_complete


def test_new_source_and_spread_happen_in_same_round():
    graph = nx.path_graph(3)

    result = simulate(graph, [0, 2])

    assert result.rounds[1].source == 2
    assert result.rounds[1].spread_vertices == frozenset({1})
    assert result.rounds[1].newly_burned == frozenset({1, 2})
    assert result.is_complete


def test_incomplete_simulation():
    graph = nx.path_graph(5)

    result = simulate(graph, [0])

    assert not result.is_complete
    assert result.burned_count == 1
    assert result.unburned_count == 4
    assert result.burning_number_candidate is None


def test_source_already_burned_is_rejected():
    graph = nx.path_graph(3)

    with pytest.raises(BurningSimulationError, match="already burned"):
        simulate(graph, [0, 0])


def test_source_not_in_graph_is_rejected():
    graph = nx.path_graph(3)

    with pytest.raises(BurningSimulationError, match="does not belong"):
        simulate(graph, [5])


def test_empty_source_sequence_on_nonempty_graph():
    graph = nx.path_graph(3)

    with pytest.raises(BurningSimulationError, match="cannot be empty"):
        simulate(graph, [])


def test_empty_graph_with_empty_sequence():
    graph = nx.Graph()

    result = simulate(graph, [])

    assert result.is_complete
    assert result.number_of_rounds == 0
    assert result.burned_count == 0


def test_disconnected_graph():
    graph = nx.Graph()
    graph.add_edges_from([(0, 1), (2, 3)])

    result = simulate(graph, [0, 2])

    assert result.is_complete
    assert result.number_of_rounds == 2
    assert result.burned_vertices == frozenset({0, 1, 2, 3})


def test_directed_graph_is_rejected():
    graph = nx.DiGraph()
    graph.add_edge(0, 1)

    with pytest.raises(BurningSimulationError, match="undirected"):
        simulate(graph, [0])


def test_self_loop_is_rejected():
    graph = nx.Graph()
    graph.add_edge(0, 0)

    with pytest.raises(BurningSimulationError, match="self-loops"):
        simulate(graph, [0])


def test_source_can_be_reached_by_spread_in_same_round():
    graph = nx.path_graph(3)

    result = simulate(graph, [0, 1])

    assert result.rounds[1].source == 1
    assert result.rounds[1].spread_vertices == frozenset({1})
    assert result.rounds[1].newly_burned == frozenset({1})
    assert result.rounds[1].burned_vertices == frozenset({0, 1})
    assert not result.is_complete


def test_stop_when_all_vertices_are_burned():
    graph = nx.path_graph(2)

    result = simulate(graph, [0, 1, 0])

    assert result.is_complete
    assert result.number_of_rounds == 2
    assert result.source_sequence == (0, 1)