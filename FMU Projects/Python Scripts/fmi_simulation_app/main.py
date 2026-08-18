import sys
from PySide6.QtWidgets import QApplication
from app.main_window import MainWindow


def main():
    app = QApplication(sys.argv)

    app.setApplicationName("FMU Simulation Platform")
    app.setOrganizationName("Cedric's Control System Projects")

    window = MainWindow()
    window.show()

    # app.exec() starts the Qt event loop and blocks until the app closes.
    # sys.exit() ensures the process exit code is passed back to the OS.
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()