import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon, QFont
from PySide6.QtCore import Qt
from database.db import Database
from ui.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("高血压患者服药智能提醒与监测")
    app.setOrganizationName("HealthCare")
    app.setStyle("Fusion")

    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)

    db_path = os.path.join(str(Path.home()), ".hypertension_reminder", "data.db")
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    Database.init(db_path)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
