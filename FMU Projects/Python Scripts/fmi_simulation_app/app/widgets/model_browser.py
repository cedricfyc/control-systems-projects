from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QPushButton,
)
from PySide6.QtCore import Signal, Qt


class ModelBrowserWidget(QWidget):
    """
    Shows loaded FMUs (and eventually, their variables) in a tree view.
    """

    # Signals emitted so MainWindow can react without ModelBrowserWidget
    # needing to know about FmuManager directly.
    add_fmu_requested = Signal()
    # Emits the fmu_id to remove
    remove_fmu_requested = Signal(str)
    # Emits the fmu_id that was selected
    fmu_selected = Signal(str)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Tree showing loaded FMUs. Each top-level item is an FMU
        # Children can be added later to show variables.
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Model/Variable", "Type"])
        layout.addWidget(self.tree)

        # Row of buttons under the tree
        button_row = QHBoxLayout()
        self.add_button = QPushButton("Add FMU")
        self.remove_button = QPushButton("Remove FMU")
        button_row.addWidget(self.add_button)
        button_row.addWidget(self.remove_button)
        layout.addLayout(button_row)

    def _connect_signals(self) -> None:
        self.add_button.clicked.connect(self._on_add_clicked)
        self.remove_button.clicked.connect(self._on_remove_clicked)
        self.tree.itemSelectionChanged.connect(self._on_selection_changed)

    # --- Internal slots: translate raw widget events into semantic signals ---

    def _on_add_clicked(self) -> None:
        self.add_fmu_requested.emit()

    def _on_remove_clicked(self) -> None:
        item = self.tree.currentItem()
        if item is not None:
            # Qt.ItemDataRole.UserRole is the standard role for stashing
            # custom data (here fmu_id) on a tree item.
            fmu_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.remove_fmu_requested.emit(fmu_id)

    def _on_selection_changed(self) -> None:
        item = self.tree.currentItem()
        if item is not None:
            fmu_id = item.data(0, Qt.ItemDataRole.UserRole)
            self.fmu_selected.emit(fmu_id)

    # --- Public API used by MainWindow to update this widget's contents ---

    def add_fmu_item(self, fmu_id: str, display_name: str) -> None:
        """
        Add a top-level tree entry representing a loaded FMU.
        Parameters
        ----------
        fmu_id
        display_name

        Returns
        -------

        """
        item = QTreeWidgetItem([display_name, "FMU"])
        # Stash the id for later retrieval
        item.setData(0, Qt.ItemDataRole.UserRole, fmu_id)
        self.tree.addTopLevelItem(item)

    def clear(self) -> None:
        """Remove all items from the tree (e.g. on New Project)."""
        self.tree.clear()