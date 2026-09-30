"""Interface de comparaison des stratégies de Graph Burning."""

from __future__ import annotations

import csv
from typing import Optional

import networkx as nx

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QFileDialog,
    QMessageBox,
    QGroupBox,
)


class ComparisonView(QWidget):
    """Interface de comparaison des résultats des algorithmes."""

    comparison_ready = pyqtSignal(object)
    status_changed = pyqtSignal(str)

    HEADERS = [
        "Stratégie",
        "Sommets",
        "Arêtes",
        "Tours",
        "Brûlés",
        "Non brûlés",
        "Complète",
        "Temps (s)",
        "Séquence des sources",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)

        self._graph: Optional[nx.Graph] = None
        self._graph_name = "Graphe"
        self._comparison = None
        self._rows = []

        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        """Construit l'interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        self.title_label = QLabel("Comparaison des stratégies")
        self.title_label.setStyleSheet(
            "font-size: 20px; font-weight: bold;"
        )

        self.compare_button = QPushButton("Comparer les stratégies")
        self.compare_button.setObjectName("primaryButton")
        self.export_button = QPushButton("Exporter en CSV")
        self.export_button.setEnabled(False)

        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        header_layout.addWidget(self.compare_button)
        header_layout.addWidget(self.export_button)

        summary_group = QGroupBox("Résumé")
        summary_layout = QHBoxLayout(summary_group)
        summary_layout.setSpacing(24)

        self.graph_label = QLabel("Graphe : -")
        self.best_label = QLabel("Meilleure stratégie : -")
        self.rounds_label = QLabel("Nombre de tours : -")
        self.status_label = QLabel("En attente")

        summary_layout.addWidget(self.graph_label)
        summary_layout.addWidget(self.best_label)
        summary_layout.addWidget(self.rounds_label)
        summary_layout.addWidget(self.status_label)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.HEADERS))
        self.table.setHorizontalHeaderLabels(self.HEADERS)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setSelectionBehavior(
            QTableWidget.SelectRows
        )
        self.table.setSelectionMode(
            QTableWidget.SingleSelection
        )
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeToContents
        )
        header.setStretchLastSection(True)
        header.setHighlightSections(False)

        layout.addLayout(header_layout)
        layout.addWidget(summary_group)
        layout.addWidget(self.table)

    def _connect_signals(self) -> None:
        """Connecte les boutons."""
        self.compare_button.clicked.connect(
            self.run_comparison
        )
        self.export_button.clicked.connect(
            self.export_csv
        )

    def set_graph(
        self,
        graph: nx.Graph,
        graph_name: str = "Graphe",
    ) -> None:
        """Charge le graphe à comparer."""
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph doit être un graphe NetworkX.")

        if graph.is_directed():
            raise ValueError("Le graphe doit être non orienté.")

        self._graph = graph.copy()
        self._graph_name = graph_name
        self._comparison = None
        self._rows.clear()

        self.table.setRowCount(0)
        self.graph_label.setText(
            f"Graphe : {graph_name} "
            f"({graph.number_of_nodes()} sommets)"
        )
        self.best_label.setText("Meilleure stratégie : -")
        self.rounds_label.setText("Nombre de tours : -")
        self.status_label.setText("Graphe chargé")
        self.export_button.setEnabled(False)
        self.compare_button.setEnabled(
            graph.number_of_nodes() > 0
        )

    def run_comparison(self) -> None:
        """Exécute la comparaison des stratégies."""
        if self._graph is None or self._graph.number_of_nodes() == 0:
            self._set_status("Veuillez charger un graphe non vide.")
            return

        try:
            from src.comparison import GraphComparisonRunner

            self.compare_button.setEnabled(False)
            self._set_status("Comparaison en cours...")

            runner = GraphComparisonRunner()

            # Ordre attendu : nom du graphe, puis graphe.
            comparison = runner.compare_graph(
                self._graph_name,
                self._graph.copy(),
            )

            self._comparison = comparison
            self._rows = list(comparison.results)

            self._populate_table(self._rows)
            self._update_summary(comparison)

            self.export_button.setEnabled(bool(self._rows))

            self.comparison_ready.emit(comparison)
            self._set_status("Comparaison terminée")

        except Exception as exc:
            self._set_status("Échec de la comparaison.")
            QMessageBox.critical(
                self,
                "Erreur de comparaison",
                f"Impossible de comparer les stratégies.\n\n{exc}",
            )

        finally:
            self.compare_button.setEnabled(
                self._graph is not None
                and self._graph.number_of_nodes() > 0
            )

    def _populate_table(self, rows) -> None:
        """Remplit le tableau avec les résultats."""
        self.table.setRowCount(len(rows))

        for row_index, result in enumerate(rows):
            values = [
                result.strategy_name,
                result.number_of_vertices,
                result.number_of_edges,
                result.number_of_rounds,
                result.burned_count,
                result.unburned_count,
                "Oui" if result.is_complete else "Non",
                f"{result.execution_time_seconds:.6f}",
                result.source_sequence,
            ]

            for column_index, value in enumerate(values):
                item = QTableWidgetItem(str(value))

                if column_index in range(1, 8):
                    item.setTextAlignment(
                        Qt.AlignCenter
                    )

                self.table.setItem(
                    row_index,
                    column_index,
                    item,
                )

        self.table.resizeRowsToContents()

    def _update_summary(self, comparison) -> None:
        """Met à jour le résumé de comparaison."""
        best = comparison.best_complete_result

        if best is None:
            self.best_label.setText(
                "Meilleure stratégie : aucune complète"
            )
            self.rounds_label.setText(
                "Nombre de tours : -"
            )
            return

        self.best_label.setText(
            f"Stratégie complète : {best.strategy_name}"
        )
        self.rounds_label.setText(
            f"Nombre de tours : {best.number_of_rounds}"
        )

    def export_csv(self) -> None:
        """Exporte les résultats affichés au format CSV."""
        if not self._rows:
            self._set_status("Aucun résultat à exporter.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exporter les résultats",
            f"{self._graph_name}_comparison.csv",
            "Fichiers CSV (*.csv)",
        )

        if not file_path:
            return

        try:
            with open(
                file_path,
                "w",
                newline="",
                encoding="utf-8-sig",
            ) as file:
                writer = csv.writer(file, delimiter=";")
                writer.writerow(self.HEADERS)

                for result in self._rows:
                    writer.writerow([
                        result.strategy_name,
                        result.number_of_vertices,
                        result.number_of_edges,
                        result.number_of_rounds,
                        result.burned_count,
                        result.unburned_count,
                        "Oui" if result.is_complete else "Non",
                        result.execution_time_seconds,
                        result.source_sequence,
                    ])

            self._set_status("Export CSV terminé.")

        except OSError as exc:
            QMessageBox.critical(
                self,
                "Erreur d'export",
                f"Impossible d'enregistrer le fichier.\n\n{exc}",
            )

    def _set_status(self, message: str) -> None:
        """Met à jour le statut."""
        self.status_label.setText(message)
        self.status_changed.emit(message)

    @property
    def comparison(self):
        """Retourne l'objet de comparaison courant."""
        return self._comparison

    @property
    def rows(self):
        """Retourne les lignes de résultats."""
        return list(self._rows)