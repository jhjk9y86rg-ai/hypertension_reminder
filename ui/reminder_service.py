from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QFrame, QComboBox, QTextEdit)
from PySide6.QtCore import Qt, QTimer, Signal, QObject
from PySide6.QtGui import QFont
from datetime import datetime
from database.db import Database


class ReminderDialog(QDialog):
    def __init__(self, medication, scheduled_time, parent=None):
        super().__init__(parent)
        self.medication = medication
        self.scheduled_time = scheduled_time
        self.setWindowTitle("⏰ 服药提醒")
        self.setMinimumWidth(420)
        self.setModal(False)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(25, 25, 25, 25)

        self.setStyleSheet("""
            QDialog {
                background-color: #fff8e1;
            }
            QPushButton#taken {
                background-color: #4caf50;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#taken:hover { background-color: #45a049; }
            QPushButton#later {
                background-color: #ff9800;
                color: white;
                padding: 10px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton#later:hover { background-color: #e68a00; }
        """)

        icon = QLabel("💊⏰")
        icon_font = QFont()
        icon_font.setPointSize(36)
        icon.setFont(icon_font)
        icon.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon)

        title = QLabel("服药时间到！")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(8)

        name_row = QLabel(f"💊 药品：<b>{self.medication['name']}</b>")
        name_font = QFont()
        name_font.setPointSize(12)
        name_row.setFont(name_font)
        info_layout.addWidget(name_row)

        dosage_row = QLabel(f"📐 剂量：<b>{self.medication['dosage']}</b>")
        dosage_row.setFont(name_font)
        info_layout.addWidget(dosage_row)

        time_row = QLabel(f"⏱️ 计划时间：<b>{self.scheduled_time}</b>")
        time_row.setFont(name_font)
        info_layout.addWidget(time_row)

        now_row = QLabel(f"🕐 当前时间：<b>{datetime.now().strftime('%H:%M:%S')}</b>")
        now_row.setFont(name_font)
        info_layout.addWidget(now_row)

        if self.medication.get("notes"):
            notes_row = QLabel(f"📝 注意：{self.medication['notes']}")
            notes_row.setWordWrap(True)
            notes_row.setStyleSheet("color: #d32f2f; padding: 8px; background: #ffebee; border-radius: 4px;")
            info_layout.addWidget(notes_row)

        layout.addLayout(info_layout)

        btns = QHBoxLayout()
        btns.addStretch()
        taken_btn = QPushButton("✓ 已服药")
        taken_btn.setObjectName("taken")
        taken_btn.setMinimumWidth(130)
        taken_btn.setMinimumHeight(42)
        taken_btn.clicked.connect(self._on_taken)
        later_btn = QPushButton("⏱ 稍后提醒")
        later_btn.setObjectName("later")
        later_btn.setMinimumWidth(130)
        later_btn.setMinimumHeight(42)
        later_btn.clicked.connect(self._on_later)
        btns.addWidget(taken_btn)
        btns.addWidget(later_btn)
        btns.addStretch()
        layout.addLayout(btns)

    def _on_taken(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.add_medication_record(
            self.medication["id"], self.medication["name"],
            self.medication["dosage"], self.scheduled_time,
            "taken", now, "按时服药"
        )
        self.accept()

    def _on_later(self):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        Database.add_medication_record(
            self.medication["id"], self.medication["name"],
            self.medication["dosage"], self.scheduled_time,
            "delayed", now, "稍后提醒"
        )
        self.accept()


class ReminderService(QObject):
    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._parent = parent
        self.timer = QTimer()
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.check_reminders)
        self._triggered_keys = set()
        self.active_dialogs = []

    def start(self):
        self.timer.start()
        self.check_reminders()

    def stop(self):
        self.timer.stop()

    def check_reminders(self):
        now = datetime.now()
        today = now.strftime("%Y-%m-%d")
        current_time = now.strftime("%H:%M")

        meds = Database.get_all_medications()
        for med in meds:
            for t in med["times"]:
                key = f"{today}_{med['id']}_{t}"
                if key in self._triggered_keys:
                    continue
                if t == current_time or self._is_time_passed(t, current_time):
                    if self._should_trigger(today, med["id"], t):
                        self._triggered_keys.add(key)
                        scheduled_full = f"{today} {t}:00"
                        dialog = ReminderDialog(med, scheduled_full, self._parent)
                        dialog.finished.connect(lambda _=None, d=dialog: self._on_dialog_closed(d))
                        self.active_dialogs.append(dialog)
                        dialog.show()
                        dialog.raise_()
                        dialog.activateWindow()

    def _is_time_passed(self, scheduled: str, current: str) -> bool:
        try:
            s_h, s_m = map(int, scheduled.split(":"))
            c_h, c_m = map(int, current.split(":"))
            s_total = s_h * 60 + s_m
            c_total = c_h * 60 + c_m
            return 0 <= (c_total - s_total) <= 1
        except Exception:
            return False

    def _should_trigger(self, today: str, med_id: int, time_str: str) -> bool:
        scheduled_full = f"{today} {time_str}:00"
        records = Database.get_records_by_date(today)
        for r in records:
            if r["medication_id"] == med_id and r["scheduled_time"] == scheduled_full:
                return False
        return True

    def _on_dialog_closed(self, dialog):
        if dialog in self.active_dialogs:
            self.active_dialogs.remove(dialog)
        try:
            self.data_changed.emit()
        except Exception:
            pass
