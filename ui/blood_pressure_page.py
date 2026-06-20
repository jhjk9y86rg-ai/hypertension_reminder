from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                                 QPushButton, QSpinBox, QLineEdit, QTextEdit,
                                 QTableWidget, QTableWidgetItem, QHeaderView,
                                 QAbstractItemView, QFrame, QMessageBox,
                                 QDateTimeEdit, QComboBox)
from PySide6.QtCore import Qt, QDateTime, QSize
from PySide6.QtGui import QColor, QBrush, QFont
from datetime import datetime
from database.db import Database

import matplotlib
matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from matplotlib import rcParams

rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'Arial Unicode MS']
rcParams['axes.unicode_minus'] = False


class BloodPressurePage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(14)
        layout.setContentsMargins(20, 20, 20, 20)

        title = QLabel("🩺 血压监测与趋势")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)

        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)

        content = QHBoxLayout()
        content.setSpacing(15)

        # 左侧：录入 + 列表
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)

        form_box = QFrame()
        form_box.setFrameShape(QFrame.StyledPanel)
        form_layout = QVBoxLayout(form_box)
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(15, 15, 15, 15)

        form_title = QLabel("📝 录入新的血压数据")
        ft_font = QFont()
        ft_font.setBold(True)
        form_title.setFont(ft_font)
        form_layout.addWidget(form_title)

        time_row = QHBoxLayout()
        time_label = QLabel("测量时间：")
        time_label.setFixedWidth(80)
        self.time_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.time_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.time_edit.setCalendarPopup(True)
        time_row.addWidget(time_label)
        time_row.addWidget(self.time_edit, 1)
        form_layout.addLayout(time_row)

        bp_row = QHBoxLayout()
        sys_label = QLabel("收缩压：")
        sys_label.setFixedWidth(60)
        self.sys_spin = QSpinBox()
        self.sys_spin.setRange(60, 260)
        self.sys_spin.setValue(120)
        self.sys_spin.setSuffix(" mmHg")
        dia_label = QLabel("舒张压：")
        dia_label.setFixedWidth(60)
        self.dia_spin = QSpinBox()
        self.dia_spin.setRange(40, 180)
        self.dia_spin.setValue(80)
        self.dia_spin.setSuffix(" mmHg")
        bp_row.addWidget(sys_label)
        bp_row.addWidget(self.sys_spin, 1)
        bp_row.addWidget(dia_label)
        bp_row.addWidget(self.dia_spin, 1)
        form_layout.addLayout(bp_row)

        pulse_row = QHBoxLayout()
        pulse_label = QLabel("脉搏：")
        pulse_label.setFixedWidth(80)
        self.pulse_spin = QSpinBox()
        self.pulse_spin.setRange(0, 220)
        self.pulse_spin.setValue(75)
        self.pulse_spin.setSuffix(" 次/分")
        self.pulse_spin.setSpecialValueText("不记录")
        pulse_row.addWidget(pulse_label)
        pulse_row.addWidget(self.pulse_spin, 1)
        form_layout.addLayout(pulse_row)

        notes_label = QLabel("备注：")
        form_layout.addWidget(notes_label)
        self.notes_edit = QLineEdit()
        self.notes_edit.setPlaceholderText("例如：空腹测量、运动后等")
        form_layout.addWidget(self.notes_edit)

        btn_row = QHBoxLayout()
        btn_row.addStretch()
        save_btn = QPushButton("💾 保存记录")
        save_btn.setMinimumWidth(120)
        save_btn.setMinimumHeight(36)
        save_btn.clicked.connect(self._add_record)
        btn_row.addWidget(save_btn)
        form_layout.addLayout(btn_row)

        left_panel.addWidget(form_box)

        list_title = QLabel("📋 最近记录")
        lt_font = QFont()
        lt_font.setBold(True)
        list_title.setFont(lt_font)
        left_panel.addWidget(list_title)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["时间", "收缩压", "舒张压", "脉搏", "备注"])
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        left_panel.addWidget(self.table, 1)

        del_btn = QPushButton("🗑️ 删除选中记录")
        del_btn.clicked.connect(self._delete_record)
        left_panel.addWidget(del_btn)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setMinimumWidth(460)
        content.addWidget(left_widget)

        # 右侧：图表
        right_panel = QVBoxLayout()

        chart_title = QLabel("📈 血压趋势图")
        ct_font = QFont()
        ct_font.setBold(True)
        chart_title.setFont(ct_font)
        right_panel.addWidget(chart_title)

        self.figure = Figure(figsize=(8, 5), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        right_panel.addWidget(self.canvas, 1)

        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("background: #e3f2fd; padding: 12px; border-radius: 6px;")
        self.summary_label.setWordWrap(True)
        right_panel.addWidget(self.summary_label)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        content.addWidget(right_widget, 1)

        layout.addLayout(content, 1)

    def refresh(self):
        self._load_table()
        self._draw_chart()

    def _load_table(self):
        records = Database.get_all_blood_pressure()
        self.table.setRowCount(min(len(records), 50))
        for idx, r in enumerate(records[:50]):
            self.table.setItem(idx, 0, QTableWidgetItem(str(r["measurement_time"])))
            sys_item = QTableWidgetItem(str(r["systolic"]))
            dia_item = QTableWidgetItem(str(r["diastolic"]))
            self._color_bp_item(sys_item, r["systolic"], r["diastolic"])
            self._color_bp_item(dia_item, r["systolic"], r["diastolic"])
            self.table.setItem(idx, 1, sys_item)
            self.table.setItem(idx, 2, dia_item)
            pulse_val = str(r["pulse"]) if r["pulse"] and r["pulse"] > 0 else "-"
            self.table.setItem(idx, 3, QTableWidgetItem(pulse_val))
            self.table.setItem(idx, 4, QTableWidgetItem(r.get("notes", "") or ""))
            for col in range(5):
                item = self.table.item(idx, col)
                if item:
                    item.setTextAlignment(Qt.AlignCenter)

    def _color_bp_item(self, item, systolic, diastolic):
        if systolic >= 140 or diastolic >= 90:
            item.setForeground(QBrush(QColor("#c62828")))
        elif systolic >= 130 or diastolic >= 85:
            item.setForeground(QBrush(QColor("#ef6c00")))
        elif systolic < 90 or diastolic < 60:
            item.setForeground(QBrush(QColor("#1565c0")))
        else:
            item.setForeground(QBrush(QColor("#2e7d32")))
        font = QFont()
        font.setBold(True)
        item.setFont(font)

    def _draw_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        records = Database.get_all_blood_pressure()
        records_sorted = sorted(records, key=lambda x: x["measurement_time"])
        recent = records_sorted[-30:] if len(records_sorted) > 30 else records_sorted

        if not recent:
            ax.text(0.5, 0.5, "暂无数据，请先录入血压记录",
                    ha="center", va="center", fontsize=14, color="#666")
            ax.set_xticks([])
            ax.set_yticks([])
            for spine in ax.spines.values():
                spine.set_visible(False)
            self.canvas.draw()
            self._update_summary([])
            return

        x_labels = []
        systolic_vals = []
        diastolic_vals = []
        for r in recent:
            try:
                dt_str = str(r["measurement_time"])
                if " " in dt_str:
                    label = dt_str[5:16]
                else:
                    label = dt_str
            except Exception:
                label = str(r["measurement_time"])
            x_labels.append(label)
            systolic_vals.append(r["systolic"])
            diastolic_vals.append(r["diastolic"])

        x_pos = list(range(len(x_labels)))

        ax.axhline(y=140, color="#e53935", linestyle="--", linewidth=1, alpha=0.6, label="收缩压警戒线(140)")
        ax.axhline(y=90, color="#e53935", linestyle="--", linewidth=1, alpha=0.6, label="舒张压警戒线(90)")
        ax.axhline(y=90, color="#ff9800", linestyle=":", linewidth=1, alpha=0.4)
        ax.axhline(y=60, color="#ff9800", linestyle=":", linewidth=1, alpha=0.4)

        ax.plot(x_pos, systolic_vals, marker="o", color="#d32f2f", linewidth=2,
                markersize=7, label="收缩压", markerfacecolor="#ffffff", markeredgewidth=2)
        ax.plot(x_pos, diastolic_vals, marker="s", color="#1976d2", linewidth=2,
                markersize=7, label="舒张压", markerfacecolor="#ffffff", markeredgewidth=2)

        ax.fill_between(x_pos, systolic_vals, diastolic_vals, alpha=0.15, color="#90caf9")

        for i, v in enumerate(systolic_vals):
            ax.annotate(str(v), (x_pos[i], v), textcoords="offset points",
                        xytext=(0, 10), ha="center", fontsize=8, color="#d32f2f", fontweight="bold")
        for i, v in enumerate(diastolic_vals):
            ax.annotate(str(v), (x_pos[i], v), textcoords="offset points",
                        xytext=(0, -12), ha="center", fontsize=8, color="#1976d2", fontweight="bold")

        ax.set_xlabel("测量时间", fontsize=11)
        ax.set_ylabel("血压 (mmHg)", fontsize=11)
        ax.set_title(f"血压趋势（最近{len(recent)}次）", fontsize=13, fontweight="bold")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(x_labels, rotation=30, ha="right", fontsize=8)
        ax.set_ylim(40, 200)
        ax.grid(True, alpha=0.3, linestyle="-")
        ax.legend(loc="upper right", fontsize=9)

        self.figure.tight_layout()
        self.canvas.draw()
        self._update_summary(records_sorted)

    def _update_summary(self, records):
        if not records:
            self.summary_label.setText("📊 暂无血压数据")
            return
        systolic_vals = [r["systolic"] for r in records]
        diastolic_vals = [r["diastolic"] for r in records]
        avg_sys = int(sum(systolic_vals) / len(systolic_vals))
        avg_dia = int(sum(diastolic_vals) / len(diastolic_vals))
        max_sys = max(systolic_vals)
        min_sys = min(systolic_vals)
        max_dia = max(diastolic_vals)
        min_dia = min(diastolic_vals)

        high_count = sum(1 for r in records if r["systolic"] >= 140 or r["diastolic"] >= 90)
        normal_count = sum(1 for r in records if 90 <= r["systolic"] < 140 and 60 <= r["diastolic"] < 90)

        status = "正常"
        status_color = "#2e7d32"
        if avg_sys >= 140 or avg_dia >= 90:
            status = "偏高，建议咨询医生"
            status_color = "#c62828"
        elif avg_sys >= 130 or avg_dia >= 85:
            status = "正常偏高，注意监测"
            status_color = "#ef6c00"

        self.summary_label.setText(
            f"<b>📊 综合分析</b> | 总测量次数: {len(records)} 次<br>"
            f"<b>平均血压:</b> {avg_sys}/{avg_dia} mmHg &nbsp;|&nbsp; "
            f"<b>最高:</b> {max_sys}/{max_dia} &nbsp;|&nbsp; "
            f"<b>最低:</b> {min_sys}/{min_dia}<br>"
            f"<b>偏高次数:</b> {high_count} 次 &nbsp;|&nbsp; "
            f"<b>正常次数:</b> {normal_count} 次 &nbsp;|&nbsp; "
            f"<b>整体状态:</b> <span style='color:{status_color};'>{status}</span>"
        )

    def _add_record(self):
        systolic = self.sys_spin.value()
        diastolic = self.dia_spin.value()
        if systolic <= diastolic:
            QMessageBox.warning(self, "输入错误", "收缩压必须大于舒张压")
            return
        pulse = self.pulse_spin.value()
        if pulse == 0:
            pulse = None
        measurement_time = self.time_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss")
        notes = self.notes_edit.text().strip()
        Database.add_blood_pressure(systolic, diastolic, pulse, measurement_time, notes)
        self.notes_edit.clear()
        self.time_edit.setDateTime(QDateTime.currentDateTime())
        self.refresh()

    def _delete_record(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.information(self, "提示", "请先选择要删除的记录")
            return
        records = Database.get_all_blood_pressure()
        if row >= len(records):
            return
        bp_id = records[row]["id"]
        reply = QMessageBox.question(self, "确认删除", "确定删除该条血压记录吗？",
                                      QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            Database.delete_blood_pressure(bp_id)
            self.refresh()
