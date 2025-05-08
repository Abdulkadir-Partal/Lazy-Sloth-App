#çalışmadı(sad face)
import sys
import json
import os
import time
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout, QCheckBox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

class PomodoroApp(QMainWindow):
    def __init__(self):
        super(PomodoroApp, self).__init__()

        self.setWindowTitle("Pomodoro Uygulaması")
        self.setGeometry(200, 200, 600, 500)

        self.initUI()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.start_time = None
        self.end_time = None
        self.remaining_time = None

        self.daily_work = 0
        self.unwanted_sites = []
        self.load_data()
        self.load_unwanted_sites()

        self.setup_selenium()

    def initUI(self):
        # Sekmeleri oluştur
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        # Pomodoro sekmesi
        self.pomodoro_tab = QWidget()
        self.tab_widget.addTab(self.pomodoro_tab, "Pomodoro")
        self.create_pomodoro_tab()

        # Hedefler sekmesi
        self.goals_tab = QWidget()
        self.tab_widget.addTab(self.goals_tab, "Hedefler")
        self.create_goals_tab()

        # Unwanted Sites sekmesi
        self.unwanted_sites_tab = QWidget()
        self.tab_widget.addTab(self.unwanted_sites_tab, "Unwanted Sites")
        self.create_unwanted_sites_tab()

    def create_pomodoro_tab(self):
        layout = QVBoxLayout()

        self.lbl_timer = QLabel("00:00", self)
        self.lbl_timer.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.lbl_timer)

        self.txt_time = QLineEdit(self)
        self.txt_time.setPlaceholderText("Süre (dakika)")
        layout.addWidget(self.txt_time)

        self.btn_start = QPushButton("Başlat", self)
        self.btn_start.clicked.connect(self.start_pomodoro)
        layout.addWidget(self.btn_start)

        self.btn_stop = QPushButton("Durdur", self)
        self.btn_stop.clicked.connect(self.stop_pomodoro)
        layout.addWidget(self.btn_stop)

        self.btn_report = QPushButton("Haftalık Rapor", self)
        self.btn_report.clicked.connect(self.show_report)
        layout.addWidget(self.btn_report)

        self.txt_report = QTextEdit(self)
        self.txt_report.setReadOnly(True)
        layout.addWidget(self.txt_report)

        self.pomodoro_tab.setLayout(layout)

    def create_goals_tab(self):
        layout = QVBoxLayout()

        self.goal_checkboxes = []
        self.days_of_week = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi', 'Pazar']

        self.goal_inputs = []
        for day in self.days_of_week:
            h_layout = QHBoxLayout()

            lbl_day = QLabel(day + ":")
            h_layout.addWidget(lbl_day)

            txt_goal = QLineEdit()
            h_layout.addWidget(txt_goal)

            chk_complete = QCheckBox("Tamamlandı")
            h_layout.addWidget(chk_complete)

            self.goal_inputs.append((txt_goal, chk_complete))
            self.goal_checkboxes.append(chk_complete)

            layout.addLayout(h_layout)

        self.btn_save_goals = QPushButton("Hedefleri Kaydet", self)
        self.btn_save_goals.clicked.connect(self.save_goals)
        layout.addWidget(self.btn_save_goals)

        self.goals_tab.setLayout(layout)

        self.load_goals()

    def create_unwanted_sites_tab(self):
        layout = QVBoxLayout()

        self.txt_unwanted_site = QLineEdit(self)
        self.txt_unwanted_site.setPlaceholderText("Site Adı")
        layout.addWidget(self.txt_unwanted_site)

        self.btn_add_unwanted = QPushButton("Unwanted", self)
        self.btn_add_unwanted.clicked.connect(self.add_unwanted_site)
        layout.addWidget(self.btn_add_unwanted)

        self.lbl_unwanted_sites = QLabel("Engellenen Siteler:", self)
        layout.addWidget(self.lbl_unwanted_sites)

        self.txt_unwanted_list = QTextEdit(self)
        self.txt_unwanted_list.setReadOnly(True)
        layout.addWidget(self.txt_unwanted_list)

        self.unwanted_sites_tab.setLayout(layout)

        self.update_unwanted_list()

    def setup_selenium(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Optional: Run in headless mode
        self.driver = webdriver.Chrome(service=Service('path/to/chromedriver'), options=chrome_options)

    def update_unwanted_list(self):
        self.txt_unwanted_list.clear()
        for site in self.unwanted_sites:
            self.txt_unwanted_list.append(site)

    def add_unwanted_site(self):
        site = self.txt_unwanted_site.text()
        if site:
            self.unwanted_sites.append(site)
            self.save_unwanted_sites()
            self.update_unwanted_list()

    def start_pomodoro(self):
        try:
            minutes = int(self.txt_time.text())
            self.remaining_time = minutes * 60
            self.start_time = time.time()
            self.end_time = self.start_time + self.remaining_time
            self.timer.start(1000)
        except ValueError:
            self.lbl_timer.setText("Geçersiz süre")

    def stop_pomodoro(self):
        self.timer.stop()
        if self.remaining_time and self.start_time:
            elapsed_time = time.time() - self.start_time
            self.daily_work += elapsed_time
            self.save_data()
            self.reset_timer()

    def update_timer(self):
        if self.remaining_time is not None:
            self.remaining_time = max(0, self.end_time - time.time())
            minutes, seconds = divmod(self.remaining_time, 60)
            self.lbl_timer.setText(f"{int(minutes):02}:{int(seconds):02}")

            if self.remaining_time <= 0:
                self.timer.stop()
                self.daily_work += time.time() - self.start_time
                self.save_data()
                self.reset_timer()
                self.play_alert_sound()

    def reset_timer(self):
        self.remaining_time = None
        self.lbl_timer.setText("00:00")

    def play_alert_sound(self):
        try:
            import winsound
            winsound.Beep(1000, 1000)  # Windows beep sound
        except ImportError:
            pass  # If winsound is not available

    def load_data(self):
        if os.path.exists("work_data.json"):
            with open("work_data.json", "r") as file:
                data = json.load(file)
                today = datetime.now().strftime("%Y-%m-%d")
                if today in data:
                    self.daily_work = data[today]

    def save_data(self):
        today = datetime.now().strftime("%Y-%m-%d")
        if os.path.exists("work_data.json"):
            with open("work_data.json", "r") as file:
                data = json.load(file)
        else:
            data = {}

        data[today] = self.daily_work

        with open("work_data.json", "w") as file:
            json.dump(data, file)

    def show_report(self):
        if os.path.exists("work_data.json"):
            with open("work_data.json", "r") as file:
                data = json.load(file)

            report = ""
            today = datetime.now()
            start_of_week = today - timedelta(days=today.weekday())

            for i in range(7):
                day = (start_of_week + timedelta(days=i)).strftime("%Y-%m-%d")
                work_time = data.get(day, 0)
                hours, remainder = divmod(work_time, 3600)
                minutes, seconds = divmod(remainder, 60)
                report += f"{day}: {int(hours)} saat {int(minutes)} dakika {int(seconds)} saniye\n"

            self.txt_report.setText(report)
        else:
            self.txt_report.setText("Veri bulunamadı.")

    def save_goals(self):
        goals_data = {}
        for i, (txt_goal, chk_complete) in enumerate(self.goal_inputs):
            goals_data[self.days_of_week[i]] = {
                'goal': txt_goal.text(),
                'completed': chk_complete.isChecked()
            }

        with open("goals_data.json", "w") as file:
            json.dump(goals_data, file)

    def load_goals(self):
        if os.path.exists("goals_data.json"):
            with open("goals_data.json", "r") as file:
                goals_data = json.load(file)

            for i, (txt_goal, chk_complete) in enumerate(self.goal_inputs):
                day = self.days_of_week[i]
                if day in goals_data:
                    txt_goal.setText(goals_data[day]['goal'])
                    chk_complete.setChecked(goals_data[day]['completed'])

    def add_unwanted_site(self):
        site = self.txt_unwanted_site.text()
        if site:
            self.unwanted_sites.append(site)
            self.save_unwanted_sites()
            self.update_unwanted_list()

    def save_unwanted_sites(self):
        with open("unwanted_sites.json", "w") as file:
            json.dump(self.unwanted_sites, file)

    def load_unwanted_sites(self):
        if os.path.exists("unwanted_sites.json"):
            with open("unwanted_sites.json", "r") as file:
                self.unwanted_sites = json.load(file)

def app():
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec_())

app()
