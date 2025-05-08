import sys
import requests
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QLineEdit, QPushButton, QVBoxLayout 
from PyQt5.QtCore import Qt


api = "a2c58a5d2465372cabe5905ba7cb04f8"

class WeatherApp(QWidget):
    def __init__(self):
        super().__init__()
        self.city_label = QLabel("Enter city name: ", self)
        self.city_input = QLineEdit(self)
        self.get_weather_button = QPushButton("Get Weather", self)
        self.temperature_label = QLabel(self)
        self.emoji_label = QLabel(self)
        self.description_label = QLabel(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Weather App")
        self.setGeometry(550,250,500,700)

        vbox = QVBoxLayout()## Set all labels in a column
        vbox.addWidget(self.city_label)
        vbox.addWidget(self.city_input)
        vbox.addWidget(self.get_weather_button)
        vbox.addWidget(self.temperature_label)
        vbox.addWidget(self.emoji_label)
        vbox.addWidget(self.description_label)
        self.setLayout(vbox)

        self.setLayout(vbox)# Except weather button we get thein in line at centre
        self.city_label.setAlignment(Qt.AlignCenter)
        self.city_input.setAlignment(Qt.AlignCenter)
        self.temperature_label.setAlignment(Qt.AlignCenter)
        self.emoji_label.setAlignment(Qt.AlignCenter)
        self.description_label.setAlignment(Qt.AlignCenter)

        self.city_label.setObjectName("city_label")
        self.city_input.setObjectName("city_input")
        self.get_weather_button.setObjectName("get_weather_button")
        self.temperature_label.setObjectName("temperature_label")
        self.emoji_label.setObjectName("emoji_label")
        self.description_label.setObjectName("description_label")

        self.setStyleSheet("""
                           QLabel, QPushButton{
                               font-family: calibri;
                           }
                           QLabel#city_label{
                            font-size: 40px;
                           }
                           QLineEdit#city_input{
                            font-size: 40px;
                           }
                           QPushButton#get_weather_button{
                            font-size: 30px;
                            font-weight: bold;
                           }
                           QLabel#temperature_label{
                            font-size: 50px;
                            font-weight: bold;
                           }
                           QLabel#emoji_label{
                            font-size: 120px
                           }
                           QLabel#description_label{
                            font-size: 80px
                           }

                           """)
        self.get_weather_button.clicked.connect(self.get_weather)
        
    def get_weather(self):
        
        api_key = "a2c58a5d2465372cabe5905ba7cb04f8"
        city = self.city_input.text()
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            if data["cod"] == 200:
                self.display_weather(data)

        except requests.exceptions.HTTPError as http_error:
            if response.status_code == 400:
                self.display_error("Bad Request\nPlease chech your input")
            if response.status_code == 401:
                self.display_error("Unauthorized\nInvalid API key")
            if response.status_code == 403:
                self.display_error("Forbidden\nAccess in denied")
            if response.status_code == 404:
                self.display_error("Not Found\nCity not found")
            if response.status_code == 500:
                self.display_error("Internal Server Error\nPlease try again later")
            if response.status_code == 502:
                self.display_error("Bad Gateway\nInvalid response from the server")
            if response.status_code == 503:
                self.display_error("Service Unavailable\nServer is down")
            if response.status_code == 504:
                self.display_error("Gateway Timeout\nNo response from the server")
            else:
                self.display_error(f"HTTP error occured\n{http_error}")   
        except requests.exceptions.ConnectionError:
            self.display_error("Connection Error")          
        except requests.exceptions.Timeout:
            self.display_error("Timeout Error") 
        except requests.exceptions.TooManyRedirects:
            self.display_error("Too Many Redirects") 
        except requests.exceptions.RequestException as req_error:
            self.display_error(f"Request Error:{req_error}") 


    def display_error(self, message):
        self.temperature_label.setStyleSheet("font-size: 30px;")
        self.temperature_label.setText(message)

    def display_weather(self, data):
        self.temperature_label.setStyleSheet("font-size: 75px;")
        temperature_k =  data["main"]["temp"]
        temperature_c = temperature_k-273.15

        self.temperature_label.setText(f"{temperature_c:.0f}"+" °C")

        weather_description = data["weather"][0]["description"]
        self.description_label.setText(weather_description)

        if weather_description == "broken clouds":
            self.emoji_label.setText("☁️")
        elif weather_description == "clear sky":
            self.emoji_label.setText("⭐")
        
        print(data)

        
 
if __name__ == "__main__":
    app = QApplication(sys.argv)
    wheather_app = WeatherApp()
    wheather_app.show()
    sys.exit(app.exec_())