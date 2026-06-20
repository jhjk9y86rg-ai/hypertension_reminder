from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QCalendarWidget, QTableWidget,
                                 QTableWidgetItem, QHeaderView, QAbstractItemView,
                                 QFrame, QGridLayout, QSizePolicy, QComboBox)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QColor, QBrush, QFont, QTextCharFormat
from calendar import monthrange
from datetime import datetime, date
from database.db import Database


class RecordPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_year = QDate.currentDate().year()
        self._current_month = QDate.currentDate().month()
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(14)
        main_layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("📅 服药记录与统计")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        main_layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        content = QHBoxLayout()
        content.setSpacing(15)

        # 左侧：日历
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        nav_row = QHBoxLayout()
        prev_btn = QPushButton("◀")
        prev_btn.setMinimumWidth(40)
        prev_btn.clicked.connect(self._prev_month)
        self.month_label = QLabel()
        month_font = QFont()
        month_font.setPointSize(14)
        month_font.setBold(True)
        self.month_label.setFont(month_font)
        self.month_label.setAlignment(Qt.AlignCenter)
        next_btn = QPushButton("▶")
        next_btn.setMinimumWidth(40)
        next_btn.clicked.connect(self._next_month)
        today_btn = QPushButton("今天")
        today_btn.clicked.connect(self._go_today)
        nav_row.addWidget(prev_btn)
        nav_row.addWidget(self.month_label, 1)
        nav_row.addWidget(next_btn)
        nav_row.addWidget(today_btn)
        left_panel.addLayout(nav_row)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendar.clicked.connect(self._on_date_clicked)
        self.calendar.setMinimumHeight(320)
        left_panel.addWidget(self.calendar)

        legend = QLabel("🟩 已服药 &nbsp; 🟧 稍后提醒 &nbsp; ⬜ 无记录")
        legend.setStyleSheet("color: #555; font-size: 11px;")
        left_panel.addWidget(legend)

        stats_box = QFrame()
        stats_box.setFrameShape(QFrame.StyledPanel)
        stats_layout = QGridLayout(stats_box)
        stats_layout.setSpacing(10)
        stats_layout.setContentsMargins(12, 12, 12, 12)
        self.total_label = QLabel("总次数: 0")
        self.taken_label = QLabel("✅ 已服药: 0")
        self.taken_label.setStyleSheet("color: #2e7d32; font-weight: bold;")
        self.delayed_label = QLabel("⏰ 稍后提醒: 0")
        self.delayed_label.setStyleSheet("color: #ef6c00; font-weight: bold;")
        self.rate_label = QLabel("📈 依从率: 0%")
        self.rate_label.setStyleSheet("color: #1565c0; font-weight: bold;")
        stats_layout.addWidget(self.total_label, 0, 0)
        stats_layout.addWidget(self.taken_label, 0, 1)
        stats_layout.addWidget(self.delayed_label, 1, 0)
        stats_layout.addWidget(self.rate_label, 1, 1)
        left_panel.addWidget(stats_box)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(420)
        content.addWidget(left_widget)

        # 右侧：当日记录
        right_panel = QVBoxLayout()
        right_panel.setSpacing(10)

        day_title = QLabel("📝 当日记录详情")
        day_title_font = QFont()
        day_title_font.setPointSize(13)
        day_title_font.setBold(True)
        day_title.setFont(day_title_font)
        right_panel.addWidget(day_title)

        self.selected_date_label = QLabel()
        self.selected_date_label.setStyleSheet("color: #666;")
        right_panel.addWidget(self.selected_date_label)

        self.record_table = QTableWidget()
        self.record_table.setColumnCount(5)
        self.record_table.setHorizontalHeaderLabels(["计划时间", "药品", "剂量", "状态", "备注"])
        self.record_table.verticalHeader().setVisible(False)
        self.record_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.record_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.record_table.setAlternatingRowColors(True)
        self.record_table.horizontalHeader().setStretchLastSection(True)
        self.record_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.record_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.record_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.record_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        right_panel.addWidget(self.record_table, 1)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        content.addWidget(right_widget, 1)

        main_layout.addLayout(content, 1)

    def refresh(self):
        self.month_label.setText(f"{self._current_year}年{self._current_month}月")
        self._highlight_calendar()
        self._load_records_for_date(self.calendar.selectedDate())
        self._update_month_stats()

    def _highlight_calendar(self):
        records = Database.get_records_by_month(self._current_year, self._current_month)
        day_stats = {}
        for r in records:
            try:
                day = int(r["scheduled_time"][8:10])
            except Exception:
                continue
            if day not in day_stats:
                day_stats[day] = {"taken": 0, "delayed": 0, "total": 0}
            day_stats[day]["total"] += 1
            if r["status"] == "taken":
                day_stats[day]["taken"] += 1
            elif r["status"] == "delayed":
                day_stats[day]["delayed"] += 1

        format_green = QTextCharFormat()
        format_green.setBackground(QBrush(QColor(200, 230, 201)))
        format_orange = QTextCharFormat()
        format_orange.setBackground(QBrush(QColor(255, 224, 178)))
        format_mixed = QTextCharFormat()
        format_mixed.setBackground(QBrush(QColor(220, 237, 200)))

        for day, stats in day_stats.items():
            qdate = QDate(self._current_year, self._current_month, day)
            if stats["taken"] > 0 and stats["delayed"] == 0:
                self.calendar.setDateTextFormat(qdate, format_green)
            elif stats["delayed"] > 0 and stats["taken"] == 0:
                self.calendar.setDateTextFormat(qdate, format_orange)
            else:
                self.calendar.setDateTextFormat(qdate, format_mixed)

    def _on_date_clicked(self, qdate):
        self._load_records_for_date(qdate)

    def _load_records_for_date(self, qdate):
        date_str = qdate.toString("yyyy-MM-dd")
        self.selected_date_label.setText(f"查看日期：{date_str}（{['周一','周二','周三','周四','周五','周六','周日'][qdate.dayOfWeek()-1]}）")
        records = Database.get_records_by_date(date_str)
        self.record_table.setRowCount(len(records))
        for row, r in enumerate(records):
            scheduled_time = r["scheduled_time"]
            time_part = scheduled_time[11:] if len(scheduled_time) > 10 else scheduled_time
            self.record_table.setItem(row, 0, QTableWidgetItem(time_part))
            self.record_table.setItem(row, 1, QTableWidgetItem(r["medication_name"]))
            self.record_table.setItem(row, 2, QTableWidgetItem(r["dosage"]))

            status_text = ""
            status_color = QColor("#666")
            if r["status"] == "taken":
                status_text = "✅ 已服药"
                status_color = QColor("#2e7d32")
            elif r["status"] == "delayed":
                status_text = "⏰ 稍后提醒"
                status_color = QColor("#ef6c00")
            elif r["status"] == "missed":
                status_text = "❌ 漏服"
                status_color = QColor("#c62828")
            status_item = QTableWidgetItem(status_text)
            status_item.setForeground(QBrush(status_color))
            self.record_table.setItem(row, 3, status_item)
            self.record_table.setItem(row, 4, QTableWidgetItem(r.get("notes", "") or ""))
            for col in range(5):
                item = self.record_table.item(row, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

    def _update_month_stats(self):
        records = Database.get_records_by_month(self._current_year, self._current_month)
        total = len(records)
        taken = sum(1 for r in records if r["status"] == "taken")
        delayed = sum(1 for r in records if r["status"] == "delayed")
        rate = int((taken / total * 100)) if total > 0 else 0
        self.total_label.setText(f"📊 总次数: {total}")
        self.taken_label.setText(f"✅ 已服药: {taken}")
        self.delayed_label.setText(f"⏰ 稍后提醒: {delayed}")
        self.rate_label.setText(f"📈 依从率: {rate}%")

    def _prev_month(self):
        self._current_month -= 1
        if self._current_month < 1:
            self._current_month = 12
            self._current_year -= 1
        self.calendar.setCurrentPage(self._current_year, self._current_month)
        self.refresh()

    def _next_month(self):
        self._current_month += 1
        if self._current_month > 12:
            self._current_month = 1
            self._current_year += 1
        self.calendar.setCurrentPage(self._current_year, self._current_month)
        self.refresh()

    def _go_today(self):
        today = QDate.currentDate()
        self._current_year = today.year()
        self._current_month = today.month()
        self.calendar.setSelectedDate(today)
        self.calendar.setCurrentPage(self._current_year, self._current_month)
        self.refresh()
