
from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Iterable

import networkx as nx


class GraphFormat(str, Enum):
    """Supported input formats."""

    ADJACENCY_MATRIX = "adjacency_matrix"
    EDGE_LIST = "edge_list"
    AUTO = "auto"


class GraphLoaderError(ValueError):
    """Raised when a graph file cannot be loaded or validated."""


class GraphLoader:
    """
    Load and validate undirected, unweighted graphs.

    Supported formats:
        - adjacency_matrix: square, symmetric binary matrix
        - edge_list: one edge per line, two integer vertex IDs

    Comments beginning with '#' and blank lines are ignored.
    """

    def load(
        self,
        path: str | Path,
        graph_format: GraphFormat | str = GraphFormat.AUTO,
    ) -> nx.Graph:
        """Load a graph from a text file."""

        file_path = Path(path)

        if not file_path.exists():
            raise GraphLoaderError(
                f"Graph file does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise GraphLoaderError(
                f"Path is not a file: {file_path}"
            )

        try:
            content = file_path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            raise GraphLoaderError(
                f"Unable to read graph file '{file_path}': {exc}"
            ) from exc

        lines = self._clean_lines(content)

        if not lines:
            raise GraphLoaderError("The graph file is empty.")

        try:
            selected_format = GraphFormat(graph_format)
        except ValueError as exc:
            supported = ", ".join(item.value for item in GraphFormat)
            raise GraphLoaderError(
                f"Unsupported graph format '{graph_format}'. "
                f"Expected one of: {supported}"
            ) from exc

        if selected_format == GraphFormat.AUTO:
            selected_format = self._detect_format(lines)

        if selected_format == GraphFormat.ADJACENCY_MATRIX:
            graph = self._parse_adjacency_matrix(lines)
        elif selected_format == GraphFormat.EDGE_LIST:
            graph = self._parse_edge_list(lines)
        else:
            raise GraphLoaderError(
                f"Unsupported graph format: {selected_format}"
            )

        graph.graph["source"] = str(file_path.resolve())
        graph.graph["format"] = selected_format.value
        graph.graph["directed"] = False
        graph.graph["weighted"] = False

        return graph

    @staticmethod
    def _clean_lines(content: str) -> list[str]:
        """Remove blank lines and full-line comments."""

        cleaned = []

        for line_number, raw_line in enumerate(
            content.splitlines(), start=1
        ):
            line = raw_line.strip()

            if not line or line.startswith("#"):
                continue

            cleaned.append(line)

        return cleaned

    def _detect_format(self, lines: list[str]) -> GraphFormat:
        """
        Detect a matrix when all rows form a square binary matrix.
        Otherwise, accept a valid two-column edge list.
        """

        rows = [line.split() for line in lines]

        if rows and all(
            all(token in {"0", "1"} for token in row)
            for row in rows
        ):
            row_lengths = {len(row) for row in rows}

            if len(row_lengths) == 1:
                width = len(rows[0])

                if width == len(rows):
                    return GraphFormat.ADJACENCY_MATRIX

        if all(len(row) == 2 for row in rows):
            return GraphFormat.EDGE_LIST

        raise GraphLoaderError(
            "Unable to detect graph format. "
            "Specify 'adjacency_matrix' or 'edge_list' explicitly."
        )

    def _parse_adjacency_matrix(
        self, lines: list[str]
    ) -> nx.Graph:
        """Parse a square, symmetric binary adjacency matrix."""

        matrix: list[list[int]] = []

        for line_number, line in enumerate(lines, start=1):
            tokens = line.split()

            try:
                row = [int(token) for token in tokens]
            except ValueError as exc:
                raise GraphLoaderError(
                    f"Invalid integer in matrix row {line_number}."
                ) from exc

            if not row:
                raise GraphLoaderError(
                    f"Matrix row {line_number} is empty."
                )

            if any(value not in (0, 1) for value in row):
                raise GraphLoaderError(
                    f"Matrix row {line_number} must contain only 0 and 1."
                )

            matrix.append(row)

        n = len(matrix)

        if n == 0:
            raise GraphLoaderError("The adjacency matrix is empty.")

        if any(len(row) != n for row in matrix):
            raise GraphLoaderError(
                "The adjacency matrix must be square."
            )

        for i in range(n):
            if matrix[i][i] != 0:
                raise GraphLoaderError(
                    f"Self-loop detected at vertex {i}: "
                    "the diagonal must contain only zeros."
                )

            for j in range(i + 1, n):
                if matrix[i][j] != matrix[j][i]:
                    raise GraphLoaderError(
                        f"Matrix is not symmetric at positions "
                        f"({i}, {j}) and ({j}, {i})."
                    )

        graph = nx.Graph()
        graph.add_nodes_from(range(n))

        for i in range(n):
            for j in range(i + 1, n):
                if matrix[i][j] == 1:
                    graph.add_edge(i, j)

        return graph

    def _parse_edge_list(self, lines: list[str]) -> nx.Graph:
        """
        Parse an edge list with two integer vertex IDs per line.

        Isolated vertices cannot be inferred from an edge list alone.
        """

        graph = nx.Graph()

        for line_number, line in enumerate(lines, start=1):
            tokens = line.split()

            if len(tokens) != 2:
                raise GraphLoaderError(
                    f"Invalid edge at line {line_number}: "
                    "expected exactly two vertex IDs."
                )

            try:
                u, v = (int(token) for token in tokens)
            except ValueError as exc:
                raise GraphLoaderError(
                    f"Invalid vertex ID at line {line_number}: "
                    "vertex IDs must be integers."
                ) from exc

            if u < 0 or v < 0:
                raise GraphLoaderError(
                    f"Negative vertex ID at line {line_number}."
                )

            if u == v:
                raise GraphLoaderError(
                    f"Self-loop detected at line {line_number}: {u} {v}."
                )

            graph.add_edge(u, v)

        if graph.number_of_nodes() == 0:
            raise GraphLoaderError(
                "The edge list does not contain any valid edges."
            )

        return graph


def load_graph(
    path: str | Path,
    graph_format: GraphFormat | str = GraphFormat.AUTO,
) -> nx.Graph:
    """Convenience function for loading a graph."""

    return GraphLoader().load(path, graph_format)