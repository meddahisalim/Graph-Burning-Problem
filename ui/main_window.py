"""Fenêtre principale de l'application Graph Burning."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import networkx as nx

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QLabel,
    QPushButton,
    QFrame,
    QMessageBox,
    QFileDialog,
    QAction,
)

from ui.dashboard import Dashboard
from ui.graph_view import GraphView
from ui.algorithm_panel import AlgorithmPanel
from ui.comparison_view import ComparisonView

# Le module graph_loader peut être à la racine du projet ou dans src/.
try:
    from src.graph_loader import load_graph as load_graph_file, GraphLoaderError
except ImportError:
    from graph_loader import load_graph as load_graph_file, GraphLoaderError


class MainWindow(QMainWindow):
    """Fenêtre principale de Graph Burning."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._graph: Optional[nx.Graph] = None
        self._graph_name = "Aucun graphe"

        self.setWindowTitle("Graph Burning")
        self.resize(1400, 850)
        self.setMinimumSize(1000, 650)

        self._build_ui()
        self._build_menu()
        self._connect_signals()
        self._update_window_status()

    # ---------------------------------------------------------
    # Construction de l'interface
    # ---------------------------------------------------------

    def _build_ui(self) -> None:
        """Construit la fenêtre et ses onglets."""
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        main_layout.setContentsMargins(16, 16, 16, 12)
        main_layout.setSpacing(14)

        self._build_header(main_layout)

        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        # Onglet Dashboard
        self.dashboard = Dashboard()
        self.tabs.addTab(self.dashboard, "Tableau de bord")

        # Onglet Simulation
        self.simulation_page = QWidget()
        simulation_layout = QHBoxLayout(self.simulation_page)
        simulation_layout.setContentsMargins(10, 12, 10, 10)
        simulation_layout.setSpacing(16)

        self.graph_view = GraphView()
        self.algorithm_panel = AlgorithmPanel()

        simulation_layout.addWidget(self.graph_view, 3)
        simulation_layout.addWidget(self.algorithm_panel, 1)

        self.tabs.addTab(self.simulation_page, "Simulation")

        # Onglet Comparaison
        self.comparison_view = ComparisonView()
        self.tabs.addTab(self.comparison_view, "Comparaison")

        main_layout.addWidget(self.tabs)

        self.setCentralWidget(central_widget)

        # Barre de statut
        self.statusBar().showMessage(
            "En attente du chargement d'un graphe."
        )

    def _build_header(self, parent_layout) -> None:
        """Construit l'en-tête de la fenêtre."""
        header = QFrame()
        header.setObjectName("mainHeader")
        header.setFrameShape(QFrame.NoFrame)

        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 14, 20, 14)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)

        self.title_label = QLabel("Graph Burning")
        self.title_label.setObjectName("mainTitle")

        self.subtitle_label = QLabel(
            "Adaptive Graph Analysis & Burning Simulation"
        )
        self.subtitle_label.setObjectName("mainSubtitle")

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        layout.addLayout(title_layout)
        layout.addStretch()

        self.graph_info_label = QLabel("Aucun graphe chargé")
        self.graph_info_label.setObjectName("graphInfo")

        self.load_graph_button = QPushButton("Charger un graphe")
        self.load_graph_button.setObjectName("primaryButton")

        layout.addWidget(self.graph_info_label)
        layout.addWidget(self.load_graph_button)

        header.setStyleSheet("""
            QFrame#mainHeader {
                background-color: #1E293B;
                border: none;
                border-radius: 4px;
            }

            QLabel#mainTitle {
                font-size: 22px;
                font-weight: bold;
                color: #F8FAFC;
            }

            QLabel#mainSubtitle {
                font-size: 12px;
                color: #94A3B8;
            }

            QLabel#graphInfo {
                color: #CBD5E1;
                padding: 0 12px;
            }
        """)

        parent_layout.addWidget(header)

    def _build_menu(self) -> None:
        """Construit les menus de l'application."""
        file_menu = self.menuBar().addMenu("Fichier")
        view_menu = self.menuBar().addMenu("Affichage")
        help_menu = self.menuBar().addMenu("Aide")

        self.action_load_graph = QAction("Charger un graphe", self)
        self.action_load_graph.setShortcut("Ctrl+O")

        self.action_exit = QAction("Quitter", self)
        self.action_exit.setShortcut("Ctrl+Q")

        self.action_dashboard = QAction("Tableau de bord", self)
        self.action_dashboard.setShortcut("Ctrl+1")

        self.action_simulation = QAction("Simulation", self)
        self.action_simulation.setShortcut("Ctrl+2")

        self.action_comparison = QAction("Comparaison", self)
        self.action_comparison.setShortcut("Ctrl+3")

        self.action_about = QAction("À propos", self)

        file_menu.addAction(self.action_load_graph)
        file_menu.addSeparator()
        file_menu.addAction(self.action_exit)

        view_menu.addAction(self.action_dashboard)
        view_menu.addAction(self.action_simulation)
        view_menu.addAction(self.action_comparison)

        help_menu.addAction(self.action_about)

    # ---------------------------------------------------------
    # Connexions
    # ---------------------------------------------------------

    def _connect_signals(self) -> None:
        """Connecte les événements de l'interface."""
        self.load_graph_button.clicked.connect(
            self._on_load_graph_requested
        )
        self.action_load_graph.triggered.connect(
            self._on_load_graph_requested
        )

        self.action_exit.triggered.connect(self.close)

        self.action_dashboard.triggered.connect(
            lambda: self.tabs.setCurrentIndex(0)
        )
        self.action_simulation.triggered.connect(
            lambda: self.tabs.setCurrentIndex(1)
        )
        self.action_comparison.triggered.connect(
            lambda: self.tabs.setCurrentIndex(2)
        )

        self.action_about.triggered.connect(self._show_about)

        # Résultat de simulation -> visualisation
        self.algorithm_panel.result_ready.connect(
            self.graph_view.set_result
        )

        # Navigation des tours -> visualisation
        self.algorithm_panel.round_changed.connect(
            self.graph_view.set_round_index
        )

        # Résultat de simulation -> Dashboard
        self.algorithm_panel.result_ready.connect(
            self._on_simulation_result
        )

        # Raccourcis du Dashboard
        self.dashboard.open_simulation_requested.connect(
            lambda: self.tabs.setCurrentIndex(1)
        )
        self.dashboard.open_comparison_requested.connect(
            lambda: self.tabs.setCurrentIndex(2)
        )

        # Statuts des composants
        self.algorithm_panel.status_changed.connect(
            self.statusBar().showMessage
        )
        self.comparison_view.status_changed.connect(
            self.statusBar().showMessage
        )

    # ---------------------------------------------------------
    # Chargement du graphe
    # ---------------------------------------------------------

    def load_graph(
        self,
        graph: nx.Graph,
        graph_name: str = "Graphe",
    ) -> None:
        """
        Charge un graphe dans tous les composants.

        Le graphe doit être non orienté.
        """
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph doit être un graphe NetworkX.")

        if graph.is_directed():
            raise ValueError("Le graphe doit être non orienté.")

        if graph.number_of_nodes() == 0:
            raise ValueError("Le graphe ne doit pas être vide.")

        self._graph = graph.copy()
        self._graph_name = graph_name

        self.graph_view.set_graph(self._graph)
        self.algorithm_panel.set_graph(self._graph)

        self.dashboard.set_graph(self._graph, graph_name)
        self.comparison_view.set_graph(self._graph, graph_name)

        self._update_window_status()

        self.statusBar().showMessage(
            f"Graphe chargé : {graph_name}"
        )

    def _on_load_graph_requested(self) -> None:
        """Ouvre un fichier, le valide avec graph_loader et l'affiche."""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Charger un graphe",
            "",
            "Fichiers de graphe (*.txt *.csv *.edges *.mat);;"
            "Tous les fichiers (*)",
        )

        if not path:  # dialogue annulé
            return

        try:
            graph = load_graph_file(path)
        except GraphLoaderError as exc:
            QMessageBox.critical(
                self,
                "Erreur de chargement",
                str(exc),
            )
            self.statusBar().showMessage(
                "Échec du chargement du graphe."
            )
            return

        try:
            self.load_graph(graph, Path(path).stem)
        except (TypeError, ValueError) as exc:
            QMessageBox.critical(
                self,
                "Graphe invalide",
                str(exc),
            )

    # ---------------------------------------------------------
    # Résultats et état
    # ---------------------------------------------------------

    def _on_simulation_result(self, result) -> None:
        """Actualise le Dashboard après une simulation."""
        strategy_name = (
            self.algorithm_panel.strategy_combo.currentText()
        )

        self.dashboard.set_result(
            result,
            strategy_name=strategy_name,
        )

        self.statusBar().showMessage(
            f"Simulation terminée : {strategy_name}"
        )

    def _update_window_status(self) -> None:
        """Actualise les informations du graphe."""
        if self._graph is None:
            self.graph_info_label.setText("Aucun graphe chargé")
            return

        self.graph_info_label.setText(
            f"{self._graph_name} | "
            f"{self._graph.number_of_nodes()} sommets | "
            f"{self._graph.number_of_edges()} arêtes"
        )

    def _show_about(self) -> None:
        """Affiche les informations sur l'application."""
        QMessageBox.about(
            self,
            "À propos de Graph Burning",
            (
                "<h3>Graph Burning</h3>"
                "<p>Application d'analyse et de simulation "
                "du problème Graph Burning.</p>"
                "<p>Stratégies : Degree, Closeness, "
                "Betweenness et comparaison.</p>"
            ),
        )