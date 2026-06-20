from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QTableWidget, QTableWidgetItem,
                                 QHeaderView, QMessageBox, QAbstractItemView,
                                 QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QBrush, QFont
from database.db import Database
from ui.medication_dialog import MedicationDialog


class MedicationPage(QWidget):
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        header = QHBoxLayout()
        title = QLabel("💊 药品管理")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        header.addWidget(title)
        header.addStretch()

        add_btn = QPushButton("➕ 新增药品")
        add_btn.setMinimumWidth(120)
        add_btn.setMinimumHeight(36)
        add_btn.clicked.connect(self._add_medication)
        header.addWidget(add_btn)

        edit_btn = QPushButton("✏️ 编辑")
        edit_btn.setMinimumWidth(100)
        edit_btn.setMinimumHeight(36)
        edit_btn.clicked.connect(self._edit_medication)
        header.addWidget(edit_btn)

        del_btn = QPushButton("🗑️ 删除")
        del_btn.setMinimumWidth(100)
        del_btn.setMinimumHeight(36)
        del_btn.clicked.connect(self._delete_medication)
        header.addWidget(del_btn)

        layout.addLayout(header)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "药品名称", "剂量", "服用时间", "注意事项"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        layout.addWidget(self.table, 1)

        self.stats_label = QLabel("")
        stats_font = QFont()
        stats_font.setPointSize(10)
        self.stats_label.setFont(stats_font)
        self.stats_label.setStyleSheet("color: #666;")
        layout.addWidget(self.stats_label)

    def refresh(self):
        meds = Database.get_all_medications()
        self.table.setRowCount(len(meds))
        for row, med in enumerate(meds):
            self.table.setItem(row, 0, QTableWidgetItem(str(med["id"])))
            self.table.setItem(row, 1, QTableWidgetItem(med["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(med["dosage"]))
            self.table.setItem(row, 3, QTableWidgetItem(", ".join(med["times"])))
            self.table.setItem(row, 4, QTableWidgetItem(med.get("notes", "") or ""))
            for col in range(5):
                item = self.table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

        self.stats_label.setText(f"📊 共 {len(meds)} 种药品登记")

    def _add_medication(self):
        dialog = MedicationDialog(self)
        if dialog.exec():
            data = dialog.result_data
            Database.add_medication(data["name"], data["dosage"], data["notes"], data["times"])
            self.refresh()
            self.data_changed.emit()

    def _edit_medication(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要编辑的药品")
            return
        med_id = int(self.table.item(row, 0).text())
        med = Database.get_medication(med_id)
        if not med:
            return
        dialog = MedicationDialog(self, med)
        if dialog.exec():
            data = dialog.result_data
            Database.update_medication(med_id, data["name"], data["dosage"], data["notes"], data["times"])
            self.refresh()
            self.data_changed.emit()

    def _delete_medication(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的药品")
            return
        med_id = int(self.table.item(row, 0).text())
        med_name = self.table.item(row, 1).text()
        reply = QMessageBox.question(self, "确认删除",
                                      f"确定删除药品【{med_name}】吗？\n相关记录不会被删除。",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            Database.delete_medication(med_id)
            self.refresh()
            self.data_changed.emit()
