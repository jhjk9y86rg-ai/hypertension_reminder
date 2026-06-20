from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QLineEdit, QTextEdit, QTimeEdit, QPushButton,
                                 QListWidget, QListWidgetItem, QMessageBox,
                                 QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QTime, Signal
from PySide6.QtGui import QFont, QIcon


class MedicationDialog(QDialog):
    def __init__(self, parent=None, medication=None):
        super().__init__(parent)
        self.medication = medication
        self._times = []
        if medication and medication.get("times"):
            self._times = list(medication["times"])
        self.setWindowTitle("药品信息" if medication is None else "编辑药品")
        self.setMinimumWidth(480)
        self._build_ui()
        if medication:
            self.name_edit.setText(medication["name"])
            self.dosage_edit.setText(medication["dosage"])
            self.notes_edit.setText(medication.get("notes", "") or "")
            for t in self._times:
                self.time_list.addItem(t)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📋 药品信息登记")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        name_row = QHBoxLayout()
        name_label = QLabel("药品名称：")
        name_label.setFixedWidth(90)
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("例如：硝苯地平缓释片")
        name_row.addWidget(name_label)
        name_row.addWidget(self.name_edit, 1)
        layout.addLayout(name_row)

        dosage_row = QHBoxLayout()
        dosage_label = QLabel("剂量：")
        dosage_label.setFixedWidth(90)
        self.dosage_edit = QLineEdit()
        self.dosage_edit.setPlaceholderText("例如：10mg")
        dosage_row.addWidget(dosage_label)
        dosage_row.addWidget(self.dosage_edit, 1)
        layout.addLayout(dosage_row)

        notes_label = QLabel("注意事项：")
        layout.addWidget(notes_label)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("例如：饭后服用，避免与葡萄柚汁同服")
        self.notes_edit.setFixedHeight(80)
        layout.addWidget(self.notes_edit)

        time_label = QLabel("服用时间（可设置多个）：")
        layout.addWidget(time_label)

        time_row = QHBoxLayout()
        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime(8, 0))
        add_btn = QPushButton("➕ 添加")
        add_btn.clicked.connect(self._add_time)
        remove_btn = QPushButton("➖ 删除选中")
        remove_btn.clicked.connect(self._remove_time)
        time_row.addWidget(self.time_edit)
        time_row.addWidget(add_btn)
        time_row.addWidget(remove_btn)
        layout.addLayout(time_row)

        self.time_list = QListWidget()
        self.time_list.setFixedHeight(90)
        layout.addWidget(self.time_list)

        btns = QHBoxLayout()
        btns.addStretch()
        ok_btn = QPushButton("✓ 保存")
        ok_btn.setMinimumWidth(100)
        ok_btn.clicked.connect(self._accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.setMinimumWidth(100)
        cancel_btn.clicked.connect(self.reject)
        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)
        layout.addLayout(btns)

    def _add_time(self):
        t = self.time_edit.time().toString("HH:mm")
        if t not in [self.time_list.item(i).text() for i in range(self.time_list.count())]:
            self.time_list.addItem(t)

    def _remove_time(self):
        for item in self.time_list.selectedItems():
            self.time_list.takeItem(self.time_list.row(item))

    def _accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入药品名称")
            return
        if not self.dosage_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入剂量")
            return
        times = [self.time_list.item(i).text() for i in range(self.time_list.count())]
        if not times:
            QMessageBox.warning(self, "提示", "请至少添加一个服用时间")
            return
        self.result_data = {
            "name": self.name_edit.text().strip(),
            "dosage": self.dosage_edit.text().strip(),
            "notes": self.notes_edit.toPlainText().strip(),
            "times": sorted(times)
        }
        self.accept()
