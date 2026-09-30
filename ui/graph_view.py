"""Visualisation graphique du processus de Graph Burning avec PyQt5."""

from __future__ import annotations

import math
from typing import Any, Hashable, Optional

import networkx as nx

from PyQt5.QtCore import Qt, QPointF
from PyQt5.QtGui import QColor, QBrush, QPen, QFont, QPainter
from PyQt5.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QGraphicsEllipseItem,
    QGraphicsLineItem,
    QGraphicsTextItem,
    QGraphicsItem,
    QFrame,
    QMenu,
)


class _NodeItem(QGraphicsEllipseItem):
    """Sommet déplaçable à la souris ; prévient la vue quand il bouge."""

    def __init__(self, node: Hashable, radius: float, on_moved) -> None:
        super().__init__(-radius, -radius, radius * 2, radius * 2)
        self.node = node
        self.edges: list[tuple[QGraphicsLineItem, Hashable, Hashable]] = []
        self._on_moved = None

        self.setFlags(
            QGraphicsItem.ItemIsSelectable
            | QGraphicsItem.ItemIsMovable
            | QGraphicsItem.ItemSendsGeometryChanges
        )
        self.setCursor(Qt.SizeAllCursor)

        # Activé en dernier pour ne pas réagir au placement initial.
        self._on_moved = on_moved

    def itemChange(self, change, value):
        if (
            change == QGraphicsItem.ItemPositionHasChanged
            and self._on_moved is not None
        ):
            self._on_moved(self)
        return super().itemChange(change, value)


class GraphView(QGraphicsView):
    """Vue interactive d'un graphe et de son état de combustion.

    Interactions :
        - glisser un sommet : le déplacer (les arêtes suivent) ;
        - glisser le fond : déplacer la vue ;
        - molette : zoom ;
        - double-clic sur le fond : ajuster à la vue ;
        - clic droit : menu (écarter, rapprocher, réorganiser...) ;
        - touches : F ajuster, R réorganiser, + écarter, - rapprocher,
          0 réinitialiser le zoom.
    """

    NODE_RADIUS = 22.0

    COLOR_UNBURNED = QColor("#CBD5E1")
    COLOR_BURNED = QColor("#EF4444")
    COLOR_SOURCE = QColor("#F59E0B")
    COLOR_EDGE = QColor("#64748B")
    COLOR_LABEL = QColor("#0F172A")
    COLOR_BACKGROUND = QColor("#F8FAFC")

    SPREAD_FACTOR = 1.25

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        self._graph: Optional[nx.Graph] = None
        self._result: Optional[Any] = None
        self._round_index = 0
        self._layout_name = "spring"
        self._positions: dict[Hashable, tuple[float, float]] = {}
        self._node_items: dict[Hashable, _NodeItem] = {}

        self._scene = QGraphicsScene(self)
        self.setScene(self._scene)

        self.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )
        self.setBackgroundBrush(QBrush(self.COLOR_BACKGROUND))
        self.setFrameShape(QFrame.NoFrame)

        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setFocusPolicy(Qt.StrongFocus)

        self.setMinimumSize(400, 300)

    # ------------------------------------------------------------------
    # API publique
    # ------------------------------------------------------------------
    def set_graph(
        self,
        graph: nx.Graph,
        result: Optional[Any] = None,
    ) -> None:
        """Charge un graphe et, éventuellement, un résultat de simulation."""
        if not isinstance(graph, nx.Graph):
            raise TypeError("graph doit être un graphe NetworkX.")

        if graph.is_directed():
            raise ValueError("Le graphe doit être non orienté.")

        self._graph = graph.copy()
        self._result = result
        self._round_index = 0

        self._calculate_positions()
        self._draw_graph()
        self.fit_graph()

    def set_result(self, result: Optional[Any]) -> None:
        """Associe un résultat de simulation au graphe affiché."""
        self._result = result
        self._round_index = 0
        self._draw_graph()

    def set_round_index(self, round_index: int) -> None:
        """
        Affiche l'état du graphe après le tour demandé.

        - 0 : état initial, avant le premier tour ;
        - 1 : état après le premier tour ;
        - 2 : état après le deuxième tour, etc.

        Les positions déplacées à la main sont conservées.
        """
        if not isinstance(round_index, int):
            raise TypeError("round_index doit être un entier.")

        if round_index < 0:
            raise ValueError("round_index ne peut pas être négatif.")

        self._round_index = round_index
        self._draw_graph()

    def get_round_index(self) -> int:
        """Retourne l'index du tour affiché."""
        return self._round_index

    def reset_zoom(self) -> None:
        """Réinitialise le zoom."""
        self.resetTransform()

    def fit_graph(self) -> None:
        """Ajuste le graphe à la zone visible."""
        if self._scene.items():
            self.fitInView(
                self._scene.sceneRect(),
                Qt.KeepAspectRatio,
            )

    def relayout(self, layout_name: Optional[str] = None) -> None:
        """
        Recalcule les positions (annule les déplacements manuels).

        layout_name : "spring", "kamada_kawai" ou "circular".
        """
        if layout_name is not None:
            self._layout_name = layout_name

        self._calculate_positions()
        self._draw_graph()
        self.fit_graph()

    def spread_out(self, factor: Optional[float] = None) -> None:
        """Écarte les sommets les uns des autres."""
        self._scale_positions(factor or self.SPREAD_FACTOR)

    def compact(self, factor: Optional[float] = None) -> None:
        """Rapproche les sommets les uns des autres."""
        self._scale_positions(1.0 / (factor or self.SPREAD_FACTOR))

    # ------------------------------------------------------------------
    # Calculs internes
    # ------------------------------------------------------------------
    def _layout_scale(self) -> float:
        """Échelle du placement, adaptée au nombre de sommets."""
        if self._graph is None:
            return 250.0

        return max(250.0, 45.0 * math.sqrt(self._graph.number_of_nodes()))

    def _calculate_positions(self) -> None:
        """Calcule des positions stables pour les sommets."""
        self._positions.clear()

        if self._graph is None or self._graph.number_of_nodes() == 0:
            return

        scale = self._layout_scale()

        try:
            if self._layout_name == "circular":
                raw = nx.circular_layout(self._graph, scale=scale)
            elif self._layout_name == "kamada_kawai":
                raw = nx.kamada_kawai_layout(self._graph, scale=scale)
            else:
                raw = nx.spring_layout(self._graph, seed=42, scale=scale)
        except Exception:
            # Ex. : SciPy absent pour kamada_kawai.
            raw = nx.spring_layout(self._graph, seed=42, scale=scale)

        for node, position in raw.items():
            self._positions[node] = (
                float(position[0]),
                float(position[1]),
            )

    def _scale_positions(self, factor: float) -> None:
        """Multiplie les distances autour du centre du graphe."""
        if not self._positions:
            return

        cx = sum(p[0] for p in self._positions.values()) / len(self._positions)
        cy = sum(p[1] for p in self._positions.values()) / len(self._positions)

        for node, (x, y) in list(self._positions.items()):
            self._positions[node] = (
                cx + (x - cx) * factor,
                cy + (y - cy) * factor,
            )

        self._draw_graph()

    def _get_burning_state(
        self,
    ) -> tuple[set[Hashable], Optional[Hashable]]:
        """
        Retourne les sommets brûlés (cumulés) et la source du tour affiché.

        Les sommets brûlés sont accumulés sur tous les tours jusqu'au tour
        affiché : cela fonctionne que BurningRound.burned_vertices soit
        cumulatif ou limité au tour courant.
        """
        if self._result is None:
            return set(), None

        rounds = getattr(self._result, "rounds", [])

        if self._round_index == 0 or not rounds:
            return set(), None

        index = min(self._round_index, len(rounds)) - 1

        burned: set[Hashable] = set()
        for burning_round in rounds[: index + 1]:
            burned.update(getattr(burning_round, "burned_vertices", []))

        source = getattr(rounds[index], "source", None)

        return burned, source

    # ------------------------------------------------------------------
    # Dessin
    # ------------------------------------------------------------------
    def _draw_graph(self) -> None:
        """Redessine entièrement la scène (positions conservées)."""
        self._scene.clear()
        self._node_items.clear()

        if self._graph is None or self._graph.number_of_nodes() == 0:
            return

        burned_vertices, source = self._get_burning_state()

        edge_items = self._draw_edges()
        self._draw_nodes(burned_vertices, source)
        self._link_edges(edge_items)

        self._update_scene_rect()

    def _update_scene_rect(self) -> None:
        """Recalcule la zone de la scène autour des éléments."""
        self._scene.setSceneRect(
            self._scene.itemsBoundingRect().adjusted(-60, -60, 60, 60)
        )

    def _draw_edges(
        self,
    ) -> list[tuple[QGraphicsLineItem, Hashable, Hashable]]:
        """Dessine les arêtes avant les sommets."""
        edge_items: list[tuple[QGraphicsLineItem, Hashable, Hashable]] = []

        if self._graph is None:
            return edge_items

        pen = QPen(self.COLOR_EDGE, 2.0)

        for node_a, node_b in self._graph.edges():
            x1, y1 = self._positions[node_a]
            x2, y2 = self._positions[node_b]

            edge = QGraphicsLineItem(x1, y1, x2, y2)
            edge.setPen(pen)
            edge.setZValue(0)
            self._scene.addItem(edge)

            edge_items.append((edge, node_a, node_b))

        return edge_items

    def _draw_nodes(
        self,
        burned_vertices: set[Hashable],
        source: Optional[Hashable],
    ) -> None:
        """Dessine les sommets avec leur état de combustion."""
        if self._graph is None:
            return

        for node in self._graph.nodes():
            x, y = self._positions[node]

            if node == source:
                color = self.COLOR_SOURCE
            elif node in burned_vertices:
                color = self.COLOR_BURNED
            else:
                color = self.COLOR_UNBURNED

            self._draw_node(node, x, y, color)

    def _draw_node(
        self,
        node: Hashable,
        x: float,
        y: float,
        color: QColor,
    ) -> None:
        """Dessine un sommet circulaire déplaçable avec son étiquette."""
        item = _NodeItem(node, self.NODE_RADIUS, self._on_node_moved)
        item.setBrush(QBrush(color))
        item.setPen(QPen(QColor("#FFFFFF"), 2.0))
        item.setZValue(1)
        item.setPos(x, y)

        if self._graph is not None:
            item.setToolTip(
                f"Sommet {node}, degré {self._graph.degree(node)}"
            )

        self._scene.addItem(item)

        # L'étiquette est enfant du sommet : elle le suit dans ses moves.
        label = QGraphicsTextItem(str(node), item)
        label.setDefaultTextColor(self.COLOR_LABEL)
        label.setFont(QFont("Arial", 10, QFont.Bold))

        text_rect = label.boundingRect()
        label.setPos(
            -text_rect.width() / 2,
            -text_rect.height() / 2,
        )
        label.setAcceptedMouseButtons(Qt.NoButton)

        self._node_items[node] = item

    def _link_edges(
        self,
        edge_items: list[tuple[QGraphicsLineItem, Hashable, Hashable]],
    ) -> None:
        """Associe chaque arête à ses deux sommets pour la mettre à jour."""
        for edge, node_a, node_b in edge_items:
            self._node_items[node_a].edges.append((edge, node_a, node_b))
            self._node_items[node_b].edges.append((edge, node_a, node_b))

    def _on_node_moved(self, item: _NodeItem) -> None:
        """Mémorise la nouvelle position et déplace les arêtes liées."""
        pos = item.pos()
        self._positions[item.node] = (pos.x(), pos.y())

        for edge, node_a, node_b in item.edges:
            pa = self._node_items[node_a].pos()
            pb = self._node_items[node_b].pos()
            edge.setLine(pa.x(), pa.y(), pb.x(), pb.y())

    # ------------------------------------------------------------------
    # Événements
    # ------------------------------------------------------------------
    def wheelEvent(self, event) -> None:
        """Gère le zoom avec la molette."""
        zoom_factor = 1.15

        if event.angleDelta().y() > 0:
            self.scale(zoom_factor, zoom_factor)
        else:
            self.scale(1 / zoom_factor, 1 / zoom_factor)

    def mouseReleaseEvent(self, event) -> None:
        """Après un déplacement, agrandit la zone de la scène si besoin."""
        super().mouseReleaseEvent(event)
        if self._node_items:
            self._update_scene_rect()

    def mouseDoubleClickEvent(self, event) -> None:
        """Double-clic sur le fond : ajuste le graphe à la vue."""
        if self.itemAt(event.pos()) is None:
            self.fit_graph()
        else:
            super().mouseDoubleClickEvent(event)

    def keyPressEvent(self, event) -> None:
        """Raccourcis clavier de la vue."""
        key = event.key()

        if key == Qt.Key_F:
            self.fit_graph()
        elif key == Qt.Key_R:
            self.relayout()
        elif key in (Qt.Key_Plus, Qt.Key_Equal):
            self.spread_out()
        elif key == Qt.Key_Minus:
            self.compact()
        elif key == Qt.Key_0:
            self.reset_zoom()
        else:
            super().keyPressEvent(event)

    def contextMenuEvent(self, event) -> None:
        """Menu contextuel pour organiser l'affichage."""
        if self._graph is None:
            return

        menu = QMenu(self)

        menu.addAction("Ajuster à la vue (F)", self.fit_graph)
        menu.addAction("Réinitialiser le zoom (0)", self.reset_zoom)
        menu.addSeparator()
        menu.addAction("Écarter les sommets (+)", self.spread_out)
        menu.addAction("Rapprocher les sommets (-)", self.compact)
        menu.addSeparator()

        layout_menu = menu.addMenu("Réorganiser")
        layout_menu.addAction(
            "Force (spring)", lambda: self.relayout("spring")
        )
        layout_menu.addAction(
            "Kamada-Kawai", lambda: self.relayout("kamada_kawai")
        )
        layout_menu.addAction(
            "Cercle", lambda: self.relayout("circular")
        )

        menu.exec_(event.globalPos())