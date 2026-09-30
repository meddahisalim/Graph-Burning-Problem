"""Tableau de bord principal de Graph Burning."""

from __future__ import annotations

from typing import Any, Optional

import networkx as nx

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QFrame,
    QProgressBar,
    QSizePolicy,
)


class StatCard(QFrame):
    """Carte statistique réutilisable."""

    def __init__(
        self,
        title: str,
        value: str = "-",
        description: str = "",
        parent=None,
    ):
        super().__init__(parent)

        self.setObjectName("statCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Preferred,
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(8)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("statTitle")

        self.value_label = QLabel(value)
        self.value_label.setObjectName("statValue")
        self.value_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        self.description_label = QLabel(description)
        self.description_label.setObjectName("statDescription")
        self.description_label.setWordWrap(True)

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        layout.addWidget(self.description_label)

    def set_value(
        self,
        value: str | int | float,
        description: Optional[str] = None,
    ) -> None:
        """Met à jour la valeur affichée."""
        self.value_label.setText(str(value))

        if description is not None:
            self.description_label.setText(description)


class Dashboard(QWidget):
    """
    Tableau de bord de l'application.

    Signaux :
        open_simulation_requested : demande d'ouverture de la simulation.
        open_comparison_requested : demande d'ouverture de la comparaison.
    """

    open_simulation_requested = pyqtSignal()
    open_comparison_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self._graph: Optional[nx.Graph] = None
        self._result: Optional[Any] = None

        self._build_ui()
        self._connect_signals()
        self._reset_statistics()

    def _build_ui(self) -> None:
        """Construit la structure du tableau de bord."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 28, 28, 28)
        main_layout.setSpacing(24)

        # En-tête
        header_layout = QHBoxLayout()
        header_layout.setSpacing(10)

        title_layout = QVBoxLayout()

        self.title_label = QLabel("Tableau de bord")
        self.title_label.setObjectName("dashboardTitle")

        self.subtitle_label = QLabel(
            "Vue générale du graphe et des résultats de combustion."
        )
        self.subtitle_label.setObjectName("dashboardSubtitle")
        self.subtitle_label.setWordWrap(True)

        title_layout.addWidget(self.title_label)
        title_layout.addWidget(self.subtitle_label)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        self.simulation_button = QPushButton(
            "Ouvrir la simulation"
        )
        self.simulation_button.setObjectName("primaryButton")

        self.comparison_button = QPushButton(
            "Comparer les stratégies"
        )

        header_layout.addWidget(self.simulation_button)
        header_layout.addWidget(self.comparison_button)

        # Cartes statistiques
        stats_layout = QGridLayout()
        stats_layout.setSpacing(16)

        self.vertices_card = StatCard(
            "Sommets",
            description="Nombre total de sommets du graphe",
        )

        self.edges_card = StatCard(
            "Arêtes",
            description="Nombre total d'arêtes",
        )

        self.burned_card = StatCard(
            "Sommets brûlés",
            description="Sommets atteints par le feu",
        )

        self.rounds_card = StatCard(
            "Nombre de tours",
            description="Tours utilisés par la simulation",
        )

        self.unburned_card = StatCard(
            "Sommets non brûlés",
            description="Sommets restant à brûler",
        )

        self.progress_card = StatCard(
            "Progression",
            value="0 %",
            description="Pourcentage de sommets brûlés",
        )

        cards = [
            self.vertices_card,
            self.edges_card,
            self.burned_card,
            self.rounds_card,
            self.unburned_card,
            self.progress_card,
        ]

        for index, card in enumerate(cards):
            stats_layout.addWidget(
                card,
                index // 3,
                index % 3,
            )

        # Progression
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(10)

        progress_header = QHBoxLayout()

        self.progress_title = QLabel(
            "Progression de la combustion"
        )
        self.progress_title.setObjectName("sectionTitle")

        self.progress_label = QLabel("0 %")
        self.progress_label.setObjectName("progressValue")

        progress_header.addWidget(self.progress_title)
        progress_header.addStretch()
        progress_header.addWidget(self.progress_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setFixedHeight(10)

        progress_layout.addLayout(progress_header)
        progress_layout.addWidget(self.progress_bar)

        # Informations de la simulation
        simulation_layout = QVBoxLayout()
        simulation_layout.setSpacing(8)

        simulation_title = QLabel("État de la simulation")
        simulation_title.setObjectName("sectionTitle")

        self.graph_name_label = QLabel("Graphe : aucun")
        self.strategy_label = QLabel("Stratégie : -")
        self.sequence_label = QLabel("Séquence des sources : -")
        self.sequence_label.setWordWrap(True)

        self.simulation_status_label = QLabel(
            "Aucune simulation exécutée."
        )
        self.simulation_status_label.setObjectName(
            "simulationStatus"
        )

        simulation_layout.addWidget(simulation_title)
        simulation_layout.addWidget(self.graph_name_label)
        simulation_layout.addWidget(self.strategy_label)
        simulation_layout.addWidget(self.sequence_label)
        simulation_layout.addWidget(
            self.simulation_status_label
        )

        main_layout.addLayout(header_layout)
        main_layout.addLayout(stats_layout)
        main_layout.addLayout(progress_layout)
        main_layout.addLayout(simulation_layout)
        main_layout.addStretch()

        self._apply_local_styles()

    def _apply_local_styles(self) -> None:
        """Applique les styles propres au tableau de bord."""
        self.setStyleSheet("""
            QFrame#statCard {
                background-color: #1E293B;
                border: none;
                border-radius: 4px;
            }

            QLabel#statTitle {
                color: #94A3B8;
                font-size: 13px;
            }

            QLabel#statValue {
                color: #F8FAFC;
                font-size: 26px;
                font-weight: bold;
            }

            QLabel#statDescription {
                color: #94A3B8;
                font-size: 11px;
            }

            QLabel#dashboardTitle {
                color: #F8FAFC;
                font-size: 24px;
                font-weight: bold;
            }

            QLabel#dashboardSubtitle {
                color: #94A3B8;
                font-size: 13px;
            }

            QLabel#sectionTitle {
                color: #F8FAFC;
                font-size: 16px;
                font-weight: bold;
            }

            QLabel#progressValue {
                color: #60A5FA;
                font-weight: bold;
            }

            QLabel#simulationStatus {
                color: #94A3B8;
                padding-top: 6px;
            }

            QProgressBar {
                background-color: #334155;
                border: none;
                border-radius: 3px;
            }

            QProgressBar::chunk {
                background-color: #2563EB;
                border-radius: 3px;
            }
        """)

    def _connect_signals(self) -> None:
        """Connecte les boutons aux signaux."""
        self.simulation_button.clicked.connect(
            self.open_simulation_requested.emit
        )

        self.comparison_button.clicked.connect(
            self.open_comparison_requested.emit
        )

    def set_graph(
        self,
        graph: nx.Graph,
        graph_name: str = "Graphe",
    ) -> None:
        """Charge un graphe et actualise ses statistiques."""
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph doit être un graphe NetworkX.")

        if graph.is_directed():
            raise ValueError("Le graphe doit être non orienté.")

        self._graph = graph.copy()
        self._result = None

        self.graph_name_label.setText(
            f"Graphe : {graph_name}"
        )

        self.vertices_card.set_value(
            self._graph.number_of_nodes()
        )
        self.edges_card.set_value(
            self._graph.number_of_edges()
        )

        self._reset_simulation_statistics()

    def set_result(
        self,
        result: Any,
        strategy_name: Optional[str] = None,
    ) -> None:
        """Actualise les statistiques à partir d'un résultat."""
        if result is None:
            raise ValueError("Le résultat ne peut pas être None.")

        self._result = result

        total = getattr(
            result,
            "total_vertices",
            self._graph.number_of_nodes() if self._graph else 0,
        )
        burned = getattr(result, "burned_count", 0)
        unburned = getattr(result, "unburned_count", total - burned)
        rounds = getattr(result, "number_of_rounds", 0)

        progress = (
            round(burned / total * 100)
            if total > 0
            else 0
        )

        self.burned_card.set_value(burned)
        self.unburned_card.set_value(unburned)
        self.rounds_card.set_value(rounds)
        self.progress_card.set_value(f"{progress} %")

        self.progress_bar.setValue(progress)
        self.progress_label.setText(f"{progress} %")

        sequence = getattr(result, "source_sequence", ())
        self.sequence_label.setText(
            "Séquence des sources : "
            + ", ".join(map(str, sequence))
        )

        if strategy_name:
            self.strategy_label.setText(
                f"Stratégie : {strategy_name}"
            )

        is_complete = getattr(result, "is_complete", False)

        self.simulation_status_label.setText(
            "Simulation terminée : tous les sommets sont brûlés."
            if is_complete
            else "Simulation terminée : certains sommets restent non brûlés."
        )

    def _reset_statistics(self) -> None:
        """Réinitialise les statistiques."""
        self.vertices_card.set_value("-")
        self.edges_card.set_value("-")
        self._reset_simulation_statistics()

    def _reset_simulation_statistics(self) -> None:
        """Réinitialise les statistiques de combustion."""
        self.burned_card.set_value("0")
        self.unburned_card.set_value("-")
        self.rounds_card.set_value("-")
        self.progress_card.set_value("0 %")

        self.progress_bar.setValue(0)
        self.progress_label.setText("0 %")

        self.strategy_label.setText("Stratégie : -")
        self.sequence_label.setText("Séquence des sources : -")
        self.simulation_status_label.setText(
            "Aucune simulation exécutée."
        )

    @property
    def graph(self) -> Optional[nx.Graph]:
        """Retourne le graphe courant."""
        return self._graph

    @property
    def result(self):
        """Retourne le résultat courant."""
        return self._result