from PySide6.QtWidgets import (QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                                 QLabel, QStatusBar, QPushButton, QHBoxLayout,
                                 QMessageBox, QDialog, QTextEdit, QFrame)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QIcon
from datetime import datetime
from ui.medication_page import MedicationPage
from ui.record_page import RecordPage
from ui.blood_pressure_page import BloodPressurePage
from ui.reminder_service import ReminderService
from database.db import Database


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("高血压患者服药智能提醒与监测系统")
        self.setMinimumSize(1280, 780)
        self.setStyleSheet("""
            QMainWindow { background-color: #f5f7fa; }
            QTabWidget::pane { border: 1px solid #d0d7de; background: #fff; border-radius: 4px; }
            QTabBar::tab {
                background: #e8eef4;
                padding: 10px 24px;
                border: 1px solid #cfd8dc;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
                font-size: 13px;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #1565c0;
                border-bottom: 3px solid #1565c0;
                font-weight: bold;
            }
            QTabBar::tab:hover:!selected { background: #d7e3ef; }
            QPushButton {
                background: #1976d2;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover { background: #1565c0; }
            QPushButton:pressed { background: #0d47a1; }
            QTableWidget {
                background: white;
                gridline-color: #e0e0e0;
                selection-background-color: #bbdefb;
                selection-color: #0d47a1;
            }
            QHeaderView::section {
                background: #eceff1;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #cfd8dc;
                font-weight: bold;
                color: #37474f;
            }
            QTableWidget::item { padding: 6px; }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background: #1976d2;
            }
            QCalendarWidget QToolButton {
                color: white;
                background: #1976d2;
                padding: 4px;
            }
            QCalendarWidget QMenu { background: white; }
            QLineEdit, QSpinBox, QTimeEdit, QDateTimeEdit, QTextEdit {
                padding: 6px;
                border: 1px solid #cfd8dc;
                border-radius: 4px;
                background: white;
                selection-background-color: #90caf9;
            }
            QLineEdit:focus, QSpinBox:focus, QTimeEdit:focus, QDateTimeEdit:focus, QTextEdit:focus {
                border: 1px solid #1976d2;
            }
            QComboBox {
                padding: 6px;
                border: 1px solid #cfd8dc;
                border-radius: 4px;
                background: white;
            }
            QLabel { color: #263238; }
        """)

        self._build_ui()
        self._init_reminder()
        self._init_clock()

    def _build_ui(self):
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(10)
        layout.setContentsMargins(14, 14, 14, 14)

        # 顶部标题栏
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #1565c0, stop:1 #42a5f5);
                border-radius: 8px;
            }
        """)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 14, 20, 14)

        title_label = QLabel("❤️ 高血压患者服药智能提醒与监测系统")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: white;")
        header_layout.addWidget(title_label)
        header_layout.addStretch()

        self.clock_label = QLabel()
        clock_font = QFont()
        clock_font.setPointSize(12)
        clock_font.setBold(True)
        self.clock_label.setFont(clock_font)
        self.clock_label.setStyleSheet("color: white; padding: 6px 12px; background: rgba(255,255,255,0.15); border-radius: 4px;")
        header_layout.addWidget(self.clock_label)

        about_btn = QPushButton("ℹ 关于")
        about_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.2);
                color: white;
                border: 1px solid rgba(255,255,255,0.4);
                padding: 6px 14px;
                border-radius: 4px;
            }
            QPushButton:hover { background: rgba(255,255,255,0.3); }
        """)
        about_btn.clicked.connect(self._show_about)
        header_layout.addWidget(about_btn)

        layout.addWidget(header)

        # Tab 控件
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.medication_page = MedicationPage()
        self.record_page = RecordPage()
        self.bp_page = BloodPressurePage()
        self.tabs.addTab(self.medication_page, "💊 药品管理")
        self.tabs.addTab(self.record_page, "📅 服药记录")
        self.tabs.addTab(self.bp_page, "🩺 血压监测")

        self.tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tabs, 1)

        self.setCentralWidget(central)

        # 状态栏
        status = QStatusBar()
        status.setStyleSheet("background: #eceff1; color: #455a64;")
        status.showMessage("💡 提示：请确保已设置药品服用时间，系统将在指定时间自动弹出提醒。 | 数据保存在本地数据库")
        self.setStatusBar(status)

    def _init_reminder(self):
        self.reminder = ReminderService(self)
        self.reminder.data_changed.connect(self._on_data_changed)
        self.reminder.start()

    def _init_clock(self):
        self.clock_timer = QTimer()
        self.clock_timer.setInterval(1000)
        self.clock_timer.timeout.connect(self._update_clock)
        self.clock_timer.start()
        self._update_clock()

    def _update_clock(self):
        now = datetime.now()
        self.clock_label.setText(f"🕐 {now.strftime('%Y年%m月%d日 %H:%M:%S')}")

    def _on_tab_changed(self, index):
        if index == 1:
            self.record_page.refresh()
        elif index == 2:
            self.bp_page.refresh()

    def _on_data_changed(self):
        self.record_page.refresh()
        self.medication_page.refresh()

    def _show_about(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("关于")
        dialog.setMinimumWidth(500)
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(12)

        title = QLabel("高血压患者服药智能提醒与监测系统")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        version = QLabel("Version 1.0.0")
        version.setAlignment(Qt.AlignCenter)
        version.setStyleSheet("color: #666;")
        layout.addWidget(version)

        text = QTextEdit()
        text.setReadOnly(True)
        text.setHtml("""
        <div style="padding: 8px;">
        <p><b>主要功能：</b></p>
        <ul>
            <li>📋 <b>药品信息管理</b> - 登记药品名称、剂量、服用时间和注意事项</li>
            <li>⏰ <b>定时服药提醒</b> - 按时弹出提醒窗口，可标记已服药或稍后提醒</li>
            <li>📅 <b>记录与日历视图</b> - 查看每日服药情况，统计服药依从率</li>
            <li>🩺 <b>血压监测与趋势</b> - 录入血压数据，绘制趋势图并自动分析</li>
        </ul>
        <p><b>技术特点：</b></p>
        <ul>
            <li>🖥️ PySide6 跨平台桌面界面</li>
            <li>📊 Matplotlib 数据可视化</li>
            <li>🗃️ SQLite 本地数据库（数据保存在用户目录）</li>
            <li>🔔 后台定时检查与提醒机制</li>
        </ul>
        <p style="color:#666;font-size:11px;"><i>参考开源项目：Drug Reminder、MedMinder、Blood Pressure Tracker 等</i></p>
        </div>
        """)
        layout.addWidget(text, 1)

        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()
