from PySide6.QtWidgets import QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton
from PySide6.QtCore import Signal

class ParameterPanelWidget(QWidget):
    """
    Displays and edits the parameter values of the selected FMU.
    """

    # Signal emitted when user clicks Apply. The edited parameters
    # are written to the FMU accordingly.
    apply_requested = Signal()

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._build_ui()
        self._connect_signals()


    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        # Rows can be dynamically added
        # 3 starting columns
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Name", "Value", "Unit"])
        self.table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.table)

        self.apply_button = QPushButton("Apply Changes")
        layout.addWidget(self.apply_button)

    # Connect signal to button
    def _connect_signals(self) -> None:
        self.apply_button.clicked.connect(self._on_apply_clicked)

    # Emit changes application signal
    def _on_apply_clicked(self) -> None:
        self.apply_requested.emit()

    # --- Public API used by MainWindow to populate/read this widget ---

    def set_parameters(self, parameters: list) -> None:
        """
        Populate the table from a list of FmuVariable objects
        (excepts objects/dicts with .name, .start_value, .unit).

        TODO: Wire this up once FMUManager.get_model_variables() works.

        Parameters
        ----------
        parameters

        Returns
        -------

        """

        # Reset the table
        self.table.setRowCount(0)

        for param in parameters:
            # Get current row count
            row = self.table.rowCount()

            # Add a new row and populate the columns
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(getattr(param, "name", ""))))
            self.table.setItem(row, 1, QTableWidgetItem(str(getattr(param, "start_value", ""))))
            self.table.setItem(row, 2, QTableWidgetItem(str(getattr(param, "unit", ""))))


    def get_edited_values(self) -> dict:
        """
        Read the current contents of the table back out as
        {parameter_name: value_as_string}

        TODO: Add value validation/type conversion based on
        the parameter's declared data_type
        Parameters
        ----------
        self

        Returns
        -------

        """
        # Container dictionary for return
        values = {}
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            current_value_item = self.table.item(row, 1)
            if name_item is not None and current_value_item is not None:
                values[name_item.text()] = current_value_item.text()

        return values


    def clear(self) -> None:
        """
        Clear table by resetting rows
        Returns
        -------

        """
        self.table.setRowCount(0)