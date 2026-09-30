"""Panneau de contrôle des algorithmes de Graph Burning."""

from __future__ import annotations

import networkx as nx

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QSlider,
    QGroupBox,
    QMessageBox,
)

from src.greedy_degree import run_greedy_degree
from src.greedy_closeness import run_greedy_closeness
from src.greedy_betweenness import run_greedy_betweenness
from src.improvements import run_best_greedy


class AlgorithmPanel(QWidget):
    """
    Panneau de contrôle des stratégies de Graph Burning.

    Signaux :
        result_ready(object): émis après une simulation réussie.
        round_changed(int): émis lorsque le tour affiché change.
        status_changed(str): émis lorsque le statut change.
    """

    result_ready = pyqtSignal(object)
    round_changed = pyqtSignal(int)
    status_changed = pyqtSignal(str)

    STRATEGIES = {
        "Degré": run_greedy_degree,
        "Closeness": run_greedy_closeness,
        "Betweenness": run_greedy_betweenness,
        "Meilleure stratégie": run_best_greedy,
    }

    def __init__(self, parent=None):
        super().__init__(parent)

        self._graph: nx.Graph | None = None
        self._result = None
        self._active_result = None

        self._build_ui()
        self._connect_signals()
        self._set_initial_state()

    def _build_ui(self) -> None:
        """Construit l'interface du panneau."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(16)

        # Groupe : sélection de la stratégie
        strategy_group = QGroupBox("Stratégie")
        strategy_layout = QVBoxLayout(strategy_group)
        strategy_layout.setSpacing(10)

        self.strategy_combo = QComboBox()
        self.strategy_combo.addItems(list(self.STRATEGIES.keys()))

        self.run_button = QPushButton("Lancer la simulation")
        self.run_button.setObjectName("primaryButton")

        strategy_layout.addWidget(
            QLabel("Choisir un algorithme :")
        )
        strategy_layout.addWidget(self.strategy_combo)
        strategy_layout.addWidget(self.run_button)

        # Groupe : résultats
        result_group = QGroupBox("Résultats")
        result_layout = QVBoxLayout(result_group)
        result_layout.setSpacing(8)

        self.status_label = QLabel("En attente")
        self.rounds_label = QLabel("Nombre de tours : -")
        self.burned_label = QLabel("Sommets brûlés : -")
        self.unburned_label = QLabel("Sommets non brûlés : -")
        self.sequence_label = QLabel("Séquence des sources : -")
        self.sequence_label.setWordWrap(True)
        self.sequence_label.setTextInteractionFlags(
            Qt.TextSelectableByMouse
        )

        result_layout.addWidget(self.status_label)
        result_layout.addWidget(self.rounds_label)
        result_layout.addWidget(self.burned_label)
        result_layout.addWidget(self.unburned_label)
        result_layout.addWidget(self.sequence_label)

        # Groupe : navigation
        navigation_group = QGroupBox("Navigation des tours")
        navigation_layout = QVBoxLayout(navigation_group)
        navigation_layout.setSpacing(10)

        self.round_label = QLabel("Tour : 0")
        self.round_slider = QSlider(Qt.Horizontal)
        self.round_slider.setMinimum(0)
        self.round_slider.setMaximum(0)
        self.round_slider.setSingleStep(1)
        self.round_slider.setPageStep(1)
        self.round_slider.setEnabled(False)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)

        self.previous_button = QPushButton("Précédent")
        self.next_button = QPushButton("Suivant")
        self.reset_button = QPushButton("Réinitialiser")

        buttons_layout.addWidget(self.previous_button)
        buttons_layout.addWidget(self.next_button)

        navigation_layout.addWidget(self.round_label)
        navigation_layout.addWidget(self.round_slider)
        navigation_layout.addLayout(buttons_layout)
        navigation_layout.addWidget(self.reset_button)

        main_layout.addWidget(strategy_group)
        main_layout.addWidget(result_group)
        main_layout.addWidget(navigation_group)
        main_layout.addStretch()

    def _connect_signals(self) -> None:
        """Connecte les événements de l'interface."""
        self.run_button.clicked.connect(self.run_simulation)
        self.round_slider.valueChanged.connect(
            self._on_round_changed
        )
        self.previous_button.clicked.connect(
            self.previous_round
        )
        self.next_button.clicked.connect(self.next_round)
        self.reset_button.clicked.connect(self.reset_panel)

    def _set_initial_state(self) -> None:
        """Configure l'état initial du panneau."""
        self.run_button.setEnabled(False)
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(False)
        self.reset_button.setEnabled(False)

    def set_graph(self, graph: nx.Graph) -> None:
        """Associe un graphe au panneau."""
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph doit être un graphe NetworkX.")

        if graph.is_directed():
            raise ValueError("Le graphe doit être non orienté.")

        self._graph = graph.copy()
        self._result = None
        self._active_result = None

        self._clear_results()
        self.run_button.setEnabled(
            self._graph.number_of_nodes() > 0
        )
        self.reset_button.setEnabled(True)
        self._set_navigation(0)

        self._set_status(
            f"Graphe chargé : {self._graph.number_of_nodes()} sommets."
        )

    def run_simulation(self) -> None:
        """Exécute la stratégie sélectionnée."""
        if self._graph is None or self._graph.number_of_nodes() == 0:
            self._set_status("Veuillez charger un graphe non vide.")
            return

        strategy_name = self.strategy_combo.currentText()
        strategy_function = self.STRATEGIES[strategy_name]

        self.run_button.setEnabled(False)
        self._set_status(f"Exécution de : {strategy_name}...")

        try:
            result = strategy_function(self._graph.copy())

            # La stratégie d'amélioration renvoie un objet
            # ImprovementResult contenant best_result.
            active_result = getattr(result, "best_result", result)

            if active_result is None:
                raise RuntimeError(
                    "La stratégie n'a retourné aucun résultat."
                )

            self._result = result
            self._active_result = active_result

            self._update_results(active_result)

            total_rounds = active_result.number_of_rounds
            self._set_navigation(total_rounds)

            self.result_ready.emit(active_result)

            self._set_status(
                f"Simulation terminée : {strategy_name}"
            )

        except Exception as exc:
            self._set_status("Échec de la simulation.")
            QMessageBox.critical(
                self,
                "Erreur de simulation",
                f"Impossible d'exécuter la stratégie.\n\n{exc}",
            )

        finally:
            self.run_button.setEnabled(
                self._graph is not None
                and self._graph.number_of_nodes() > 0
            )

    def _update_results(self, result) -> None:
        """Met à jour les informations de résultat."""
        self.rounds_label.setText(
            f"Nombre de tours : {result.number_of_rounds}"
        )
        self.burned_label.setText(
            f"Sommets brûlés : {result.burned_count}"
        )
        self.unburned_label.setText(
            f"Sommets non brûlés : {result.unburned_count}"
        )

        sequence = getattr(result, "source_sequence", ())
        self.sequence_label.setText(
            "Séquence des sources : "
            + ", ".join(map(str, sequence))
        )

    def _clear_results(self) -> None:
        """Efface les anciens résultats."""
        self.rounds_label.setText("Nombre de tours : -")
        self.burned_label.setText("Sommets brûlés : -")
        self.unburned_label.setText("Sommets non brûlés : -")
        self.sequence_label.setText("Séquence des sources : -")

    def _set_navigation(self, total_rounds: int) -> None:
        """Configure le curseur de navigation."""
        self.round_slider.blockSignals(True)
        self.round_slider.setMinimum(0)
        self.round_slider.setMaximum(total_rounds)
        self.round_slider.setValue(0)
        self.round_slider.blockSignals(False)

        has_rounds = total_rounds > 0

        self.round_slider.setEnabled(has_rounds)
        self.previous_button.setEnabled(False)
        self.next_button.setEnabled(has_rounds)
        self.round_label.setText(f"Tour : 0 / {total_rounds}")

        self.round_changed.emit(0)

    def _on_round_changed(self, round_index: int) -> None:
        """Réagit au déplacement du curseur."""
        maximum = self.round_slider.maximum()

        self.round_label.setText(
            f"Tour : {round_index} / {maximum}"
        )

        self.previous_button.setEnabled(round_index > 0)
        self.next_button.setEnabled(round_index < maximum)

        self.round_changed.emit(round_index)

    def previous_round(self) -> None:
        """Passe au tour précédent."""
        self.round_slider.setValue(
            max(0, self.round_slider.value() - 1)
        )

    def next_round(self) -> None:
        """Passe au tour suivant."""
        self.round_slider.setValue(
            min(
                self.round_slider.maximum(),
                self.round_slider.value() + 1,
            )
        )

    def reset_panel(self) -> None:
        """Réinitialise les résultats et la navigation."""
        self._result = None
        self._active_result = None

        self._clear_results()
        self._set_navigation(0)

        self._set_status("En attente d'une simulation.")

        self.run_button.setEnabled(
            self._graph is not None
            and self._graph.number_of_nodes() > 0
        )

    def _set_status(self, message: str) -> None:
        """Met à jour le statut et émet le signal correspondant."""
        self.status_label.setText(message)
        self.status_changed.emit(message)

    @property
    def result(self):
        """Retourne le résultat brut de la stratégie."""
        return self._result

    @property
    def active_result(self):
        """Retourne le résultat de simulation exploitable."""
        return self._active_result