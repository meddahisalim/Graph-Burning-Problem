"""Système centralisé de styles pour Graph Burning."""

from __future__ import annotations

from PyQt5.QtWidgets import QApplication


class AppColors:
    """Palette de couleurs de l'application."""

    # Arrière-plans
    BACKGROUND = "#0F172A"
    SURFACE = "#1E293B"
    SURFACE_HOVER = "#334155"
    INPUT_BACKGROUND = "#111827"

    # Texte
    TEXT_PRIMARY = "#F8FAFC"
    TEXT_SECONDARY = "#94A3B8"
    TEXT_DISABLED = "#64748B"

    # Couleurs fonctionnelles
    PRIMARY = "#2563EB"
    PRIMARY_HOVER = "#1D4ED8"
    SUCCESS = "#22C55E"
    WARNING = "#F59E0B"
    DANGER = "#EF4444"

    # Bordures (utilisées seulement pour le focus)
    BORDER = "#334155"
    BORDER_FOCUS = "#3B82F6"

    # Graphe
    NODE_UNBURNED = "#CBD5E1"
    NODE_BURNED = "#EF4444"
    NODE_SOURCE = "#F59E0B"
    EDGE = "#64748B"


class AppStyles:
    """Feuilles de style QSS de l'application (design plat, sans bordures)."""

    MAIN_STYLE = f"""
        QWidget {{
            background-color: {AppColors.BACKGROUND};
            color: {AppColors.TEXT_PRIMARY};
            font-family: "Segoe UI", Arial, sans-serif;
            font-size: 13px;
        }}

        QMainWindow {{
            background-color: {AppColors.BACKGROUND};
        }}

        QLabel {{
            background-color: transparent;
            color: {AppColors.TEXT_PRIMARY};
        }}

        QGroupBox {{
            background-color: {AppColors.SURFACE};
            border: none;
            border-radius: 4px;
            margin-top: 18px;
            padding: 18px 16px 16px 16px;
            font-weight: 600;
        }}

        QGroupBox::title {{
            subcontrol-origin: margin;
            subcontrol-position: top left;
            left: 4px;
            padding: 0 4px;
            background-color: transparent;
            color: {AppColors.TEXT_PRIMARY};
        }}

        QPushButton {{
            background-color: {AppColors.SURFACE_HOVER};
            color: {AppColors.TEXT_PRIMARY};
            border: none;
            border-radius: 4px;
            padding: 10px 18px;
            min-height: 18px;
        }}

        QPushButton:hover {{
            background-color: {AppColors.TEXT_DISABLED};
        }}

        QPushButton:pressed {{
            background-color: {AppColors.INPUT_BACKGROUND};
        }}

        QPushButton:disabled {{
            background-color: {AppColors.INPUT_BACKGROUND};
            color: {AppColors.TEXT_DISABLED};
        }}

        QPushButton#primaryButton {{
            background-color: {AppColors.PRIMARY};
            color: #FFFFFF;
        }}

        QPushButton#primaryButton:hover {{
            background-color: {AppColors.PRIMARY_HOVER};
        }}

        QPushButton#primaryButton:disabled {{
            background-color: {AppColors.INPUT_BACKGROUND};
            color: {AppColors.TEXT_DISABLED};
        }}

        QPushButton#successButton {{
            background-color: {AppColors.SUCCESS};
            color: #FFFFFF;
        }}

        QPushButton#dangerButton {{
            background-color: {AppColors.DANGER};
            color: #FFFFFF;
        }}

        QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {{
            background-color: {AppColors.INPUT_BACKGROUND};
            color: {AppColors.TEXT_PRIMARY};
            border: none;
            border-radius: 4px;
            padding: 9px 10px;
            min-height: 18px;
            selection-background-color: {AppColors.PRIMARY};
        }}

        QLineEdit:focus, QComboBox:focus,
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border: 1px solid {AppColors.BORDER_FOCUS};
        }}

        QComboBox QAbstractItemView {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_PRIMARY};
            selection-background-color: {AppColors.PRIMARY};
            border: none;
            outline: none;
        }}

        QTableWidget, QTableView {{
            background-color: {AppColors.SURFACE};
            alternate-background-color: {AppColors.INPUT_BACKGROUND};
            color: {AppColors.TEXT_PRIMARY};
            gridline-color: transparent;
            border: none;
            border-radius: 4px;
            outline: none;
            selection-background-color: {AppColors.PRIMARY};
            selection-color: #FFFFFF;
        }}

        QTableWidget::item, QTableView::item {{
            padding: 6px 8px;
            border: none;
        }}

        QHeaderView::section {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_SECONDARY};
            border: none;
            padding: 12px 8px;
            font-weight: 600;
        }}

        QSlider::groove:horizontal {{
            height: 4px;
            background-color: {AppColors.SURFACE_HOVER};
            border-radius: 2px;
        }}

        QSlider::sub-page:horizontal {{
            background-color: {AppColors.PRIMARY};
            border-radius: 2px;
        }}

        QSlider::handle:horizontal {{
            background-color: {AppColors.PRIMARY};
            width: 14px;
            margin: -5px 0;
            border-radius: 7px;
        }}

        QSlider::handle:horizontal:hover {{
            background-color: {AppColors.PRIMARY_HOVER};
        }}

        QTabWidget::pane {{
            border: none;
            background-color: {AppColors.BACKGROUND};
        }}

        QTabBar {{
            qproperty-drawBase: 0;
            background-color: transparent;
        }}

        QTabBar::tab {{
            background-color: {AppColors.SURFACE};
            color: {AppColors.TEXT_SECONDARY};
            padding: 10px 20px;
            margin-right: 4px;
            border: none;
            border-top-left-radius: 4px;
            border-top-right-radius: 4px;
        }}

        QTabBar::tab:selected {{
            background-color: {AppColors.PRIMARY};
            color: #FFFFFF;
        }}

        QTabBar::tab:hover:!selected {{
            background-color: {AppColors.SURFACE_HOVER};
        }}

        QMenuBar {{
            background-color: {AppColors.BACKGROUND};
        }}

        QMenuBar::item {{
            padding: 6px 12px;
            background-color: transparent;
        }}

        QMenuBar::item:selected {{
            background-color: {AppColors.SURFACE_HOVER};
        }}

        QMenu {{
            background-color: {AppColors.SURFACE};
            border: none;
            padding: 4px;
        }}

        QMenu::item {{
            padding: 7px 26px;
            border-radius: 3px;
        }}

        QMenu::item:selected {{
            background-color: {AppColors.PRIMARY};
        }}

        QMenu::separator {{
            height: 6px;
            background-color: transparent;
        }}

        QScrollBar:vertical {{
            background-color: {AppColors.BACKGROUND};
            width: 10px;
            margin: 0;
        }}

        QScrollBar::handle:vertical {{
            background-color: {AppColors.SURFACE_HOVER};
            min-height: 30px;
            border-radius: 4px;
        }}

        QScrollBar:horizontal {{
            background-color: {AppColors.BACKGROUND};
            height: 10px;
            margin: 0;
        }}

        QScrollBar::handle:horizontal {{
            background-color: {AppColors.SURFACE_HOVER};
            min-width: 30px;
            border-radius: 4px;
        }}

        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical,
        QScrollBar::add-line:horizontal,
        QScrollBar::sub-line:horizontal {{
            height: 0;
            width: 0;
        }}

        QToolTip {{
            background-color: {AppColors.SURFACE_HOVER};
            color: {AppColors.TEXT_PRIMARY};
            border: none;
            padding: 6px 8px;
        }}
    """


def apply_app_style(app: QApplication) -> None:
    """Applique le thème sombre à l'application."""
    if not isinstance(app, QApplication):
        raise TypeError("app doit être une instance de QApplication.")

    app.setStyle("Fusion")
    app.setStyleSheet(AppStyles.MAIN_STYLE)