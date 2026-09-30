
import networkx as nx
import pytest

from src.graph_loader import (
    GraphFormat,
    GraphLoader,
    GraphLoaderError,
    load_graph,
)


@pytest.fixture
def loader():
    return GraphLoader()


def test_load_adjacency_matrix(tmp_path, loader):
    file_path = tmp_path / "graph.txt"
    file_path.write_text(
        "0 1 1\n"
        "1 0 0\n"
        "1 0 0\n",
        encoding="utf-8",
    )

    graph = loader.load(
        file_path,
        GraphFormat.ADJACENCY_MATRIX,
    )

    assert isinstance(graph, nx.Graph)
    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2
    assert set(graph.edges()) == {(0, 1), (0, 2)}


def test_load_edge_list(tmp_path, loader):
    file_path = tmp_path / "edges.txt"
    file_path.write_text(
        "0 1\n"
        "1 2\n"
        "2 3\n",
        encoding="utf-8",
    )

    graph = loader.load(file_path, GraphFormat.EDGE_LIST)

    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 3
    assert nx.is_connected(graph)


def test_auto_detect_matrix(tmp_path, loader):
    file_path = tmp_path / "matrix.txt"
    file_path.write_text(
        "0 1\n"
        "1 0\n",
        encoding="utf-8",
    )

    graph = loader.load(file_path)

    assert graph.graph["format"] == "adjacency_matrix"
    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1


def test_reject_non_square_matrix(tmp_path, loader):
    file_path = tmp_path / "bad_matrix.txt"
    file_path.write_text(
        "0 1 0\n"
        "1 0 1\n",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="square"):
        loader.load(
            file_path,
            GraphFormat.ADJACENCY_MATRIX,
        )


def test_reject_asymmetric_matrix(tmp_path, loader):
    file_path = tmp_path / "asymmetric.txt"
    file_path.write_text(
        "0 1\n"
        "0 0\n",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="not symmetric"):
        loader.load(
            file_path,
            GraphFormat.ADJACENCY_MATRIX,
        )


def test_reject_non_binary_matrix(tmp_path, loader):
    file_path = tmp_path / "weighted.txt"
    file_path.write_text(
        "0 2\n"
        "2 0\n",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="0 and 1"):
        loader.load(
            file_path,
            GraphFormat.ADJACENCY_MATRIX,
        )


def test_reject_self_loop_in_matrix(tmp_path, loader):
    file_path = tmp_path / "loop.txt"
    file_path.write_text(
        "1 0\n"
        "0 0\n",
        encoding="utf-8",
    )

    with pytest.raises(GraphLoaderError, match="Self-loop"):
        loader.load(
            file_path,
            GraphFormat.ADJACENCY_MATRIX,
        )


def test_reject_self_loop_in_edge_list(tmp_path, loader):
    file_path = tmp_path / "loop_edges.txt"
    file_path.write_text("2 2\n", encoding="utf-8")

    with pytest.raises(GraphLoaderError, match="Self-loop"):
        loader.load(file_path, GraphFormat.EDGE_LIST)


def test_reject_negative_vertex(tmp_path, loader):
    file_path = tmp_path / "negative.txt"
    file_path.write_text("-1 2\n", encoding="utf-8")

    with pytest.raises(GraphLoaderError, match="Negative"):
        loader.load(file_path, GraphFormat.EDGE_LIST)


def test_reject_missing_file(tmp_path, loader):
    file_path = tmp_path / "missing.txt"

    with pytest.raises(GraphLoaderError, match="does not exist"):
        loader.load(file_path)


def test_reject_empty_file(tmp_path, loader):
    file_path = tmp_path / "empty.txt"
    file_path.write_text("", encoding="utf-8")

    with pytest.raises(GraphLoaderError, match="empty"):
        loader.load(file_path)


def test_ignore_comments_and_blank_lines(tmp_path):
    file_path = tmp_path / "comments.txt"
    file_path.write_text(
        "# Graph example\n"
        "\n"
        "0 1\n"
        "# Another comment\n"
        "1 2\n",
        encoding="utf-8",
    )

    graph = load_graph(file_path, GraphFormat.EDGE_LIST)

    assert graph.number_of_nodes() == 3
    assert graph.number_of_edges() == 2


def test_duplicate_edges_are_not_counted_twice(tmp_path):
    file_path = tmp_path / "duplicates.txt"
    file_path.write_text(
        "0 1\n"
        "1 0\n"
        "0 1\n",
        encoding="utf-8",
    )

    graph = load_graph(file_path, GraphFormat.EDGE_LIST)

    assert graph.number_of_nodes() == 2
    assert graph.number_of_edges() == 1