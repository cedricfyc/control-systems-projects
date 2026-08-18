from datetime import datetime

from PySide6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit

class LogConsoleWidget(QWidget):
    """
    Read-only scrolling text area used as an in-app log/console
    """

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        self.text_edit = QPlainTextEdit()
        self.text_edit.setReadOnly(True)
        layout.addWidget(self.text_edit)

    def append_log(self, message: str, level: str = "INFO") -> None:
        """
        Add a timestamped line to the console.

        Args:
            message: the text to log
            level: a short tag to describe the information type e.g. "INFO", "WARNING", "ERROR", "CRITICAL
        """

        timestamp = datetime.now().strftime("%H:%M:%S")
        self.text_edit.appendPlainText(f"{timestamp}: [{level}] {message}")

    def clear(self) -> None:
        self.text_edit.clear()