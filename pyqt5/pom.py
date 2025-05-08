import sys
import time
import json
import os
from datetime import datetime, timedelta
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QLineEdit, QTextEdit

class PomodoroApp(QMainWindow):
    def __init__(self):
        super(PomodoroApp, self).__init__()

        self.setWindowTitle("Pomodoro Uygulaması")
        self.setGeometry(200, 200, 400, 300)

        self.initUI()
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.start_time = None
        self.end_time = None
        self.remaining_time = None

        self.daily_work = 0
        self.load_data()

    def initUI(self):
        self.lbl_timer = QLabel("00:00", self)
        self.lbl_timer.setAlignment(QtCore.Qt.AlignCenter)
        self.lbl_timer.setGeometry(150, 50, 100, 50)

        self.txt_time = QLineEdit(self)
        self.txt_time.setPlaceholderText("Süre (dakika)")
        self.txt_time.setGeometry(150, 120, 100, 30)

        self.btn_start = QPushButton("Başlat", self)
        self.btn_start.setGeometry(50, 170, 100, 30)
        self.btn_start.clicked.connect(self.start_pomodoro)

        self.btn_stop = QPushButton("Durdur", self)
        self.btn_stop.setGeometry(250, 170, 100, 30)
        self.btn_stop.clicked.connect(self.stop_pomodoro)

        self.btn_report = QPushButton("Haftalık Rapor", self)
        self.btn_report.setGeometry(150, 220, 100, 30)
        self.btn_report.clicked.connect(self.show_report)

        self.txt_report = QTextEdit(self)
        self.txt_report.setReadOnly(True)
        self.txt_report.setGeometry(50, 260, 300, 200)

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

    def reset_timer(self):
        self.remaining_time = None
        self.lbl_timer.setText("00:00")

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

def app():
    app = QApplication(sys.argv)
    win = PomodoroApp()
    win.show()
    sys.exit(app.exec_())

app()
