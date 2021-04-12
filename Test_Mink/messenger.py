from PyQt5 import QtWidgets, QtCore, QtGui
import clientui,settingsui
import requests
import datetime
import time
import json
import os

user_leave = False
config = {}
names = []
server_online = True
server_start = False

class Settings(QtWidgets.QMainWindow, settingsui.Ui_MainWindow):
    def __init__(self):
        global config
        super().__init__()
        self.setupUi(self)

        if config == {}:
            self.pushButton_2.pressed.connect(self.entry_without_config)
        
        else:
            self.pushButton_2.pressed.connect(self.entry)
            self.lineEdit_2.setText(config["ip_server"])
            self.lineEdit.setText(config["username"])

        self.pushButton.pressed.connect(self.get_update)
        self.setWindowIcon(QtGui.QIcon(os.getcwd() + "\\resourses\\Icon.png"))

    def entry(self):
        global config, user_leave, server_online, server_start

        with open(os.getcwd() + "\\data\\config.json") as file:
            config = json.load(file)

        new_ip = self.lineEdit_2.text()
        new_username = self.lineEdit.text()

        if new_username.strip() == "":
            self.textBrowser.setText("Имя не может быть пустым")
            return

        elif new_ip.strip() == "":
            self.textBrowser.setText("IP не может быть пустым")
            return
        
        else:
            try:
                requests.get(f"http://{new_ip}:5000/")
                server_online = False
                self.textBrowser.setText("Данные сохраненны")

                if config["ip_server"] != new_ip or config["username"] != new_username and config["username"] in names:
                    try:
                        requests.get(f"http://" + config["ip_server"] + ":5000/minus_users", json={"user_minus" : config["username"]})
                    except:
                        print("Неудалось удалить пользователя")
                    config["username"] = new_username
                    config["ip_server"] = new_ip
                    server_online = True
                    server_start = True

                config["username"] = new_username
                config["ip_server"] = new_ip

                with open(os.getcwd() + "\\data\\config.json", "w") as file:
                    json.dump(config, file, ensure_ascii=False, indent=4)

                return

            except:
                self.textBrowser.setText("Сервер не доступен или введённый IP неверный")
                return

    def entry_without_config(self):
        global config, server_online
        self.textBrowser.setText("Введите имя и IP")

        new_ip = self.lineEdit_2.text()
        new_username = self.lineEdit.text()

        if new_username.strip() == "":
            self.textBrowser.setText("Имя не может быть пустым")
            return

        elif new_ip.strip() == "":
            self.textBrowser.setText("IP не может быть пустым")
            return
        
        else:
            try:
                requests.get(f"http://{new_ip}:5000/")
                self.textBrowser.setText("Данные сохранены")

                config["username"] = new_username
                config["ip_server"] = new_ip
                server_online = True

                with open(os.getcwd() + "\\data\\config.json", "w") as file:
                    json.dump(config, file, ensure_ascii=False, indent=4)

                return

            except:
                self.textBrowser.setText("Сервер не доступен или введённый IP неверный")
                return
    
    def get_update(self):
        response = requests.get("http://" + config["ip_server"] + ":5000/get_update")
        messenger_update = response.json()["messenger_update"]
        clientui_update = response.json()["clientui_update"]
        settingsui_update = response.json()["settingsui_update"]

        if messenger_update == "" or clientui_update == "" or clientui_update == "":
            self.textBrowser.setText("Отправте обновление")

        else:
            with open("messenger.py","w",encoding="utf-8") as file:
                file.write(messenger_update)

            with open("clientui.py","w",encoding="utf-8") as file:
                file.write(clientui_update)


            with open("settingsui.py","w",encoding="utf-8") as file:
                file.write(settingsui_update)

            self.textBrowser.setText("Обновление загруженно\nДля вступления обновления в силу нужно перезапустить Mink")


class Messanger(QtWidgets.QMainWindow, clientui.Ui_MainWindow):
    def __init__(self):
        global config, server_start, server_online
        
        super().__init__()
        self.setupUi(self)
        
        try:
            with open(os.getcwd() + "\\data\\config.json") as file:
                config = json.load(file)

            self.ip = config["ip_server"]
            self.username = config["username"]

            self.lineEdit.setText(self.username)
            self.lineEdit_2.setText(self.ip)

            print(self.ip)

        except:
            self.show_settings()
            server_online = False

        self.setWindowIcon(QtGui.QIcon(os.getcwd() + "\\resourses\\Icon.png"))
        self.lineEdit.setReadOnly(True)
        self.lineEdit_2.setReadOnly(True)
        self.pushButton_3.setVisible(False)

        self.pushButton.pressed.connect(self.send_message)

        self.pushButton_2.pressed.connect(self.show_settings)

        self.pushButton_3.pressed.connect(self.set_server_online)


        self.after = 0
        self.num_messages = 0
        self.num_users = 0
        self.last_num_users = 0
        self.user_plus = ""
        self.user_minus = ""
        server_start = False

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_config)
        self.timer.start(1000)

    def set_server_online(self):
        global server_online
        server_online = True

    def update_config(self):
        try:
            with open(os.getcwd() + "\\data\\config.json") as file:
                config = json.load(file)

            self.ip = config["ip_server"]
            self.username = config["username"]
            self.lineEdit.setText(self.username)
            self.lineEdit_2.setText(self.ip)

            self.get_messages()
        
        except:
            return
        
        
    def show_settings(self):
        self.settings = Settings()
        self.settings.show()

    def print_messages(self, message):
        dt = datetime.datetime.fromtimestamp(message["time"])
        dt = dt.strftime("%H:%M:%S")
        self.textBrowser.append(dt + " " + message["username"])
        self.textBrowser.append(message["text"])
        self.textBrowser.append(" ")

    def get_messages(self):
        global names, server_online, server_start
        if server_online == True:
            try:
                response = requests.get(f"http://{self.ip}:5000/get_messages", params={"after" : self.after})

                server_online = True
                self.pushButton_3.setVisible(False)

                if server_start == True:
                    self.textBrowser.setText("")
                    server_start = False


                messages = response.json()["messages"]
                self.num_messages = response.json()["num_messages"]
                self.num_users = response.json()["num_users"]
                self.user_plus = response.json()["user_plus"]
                self.user_minus = response.json()["user_minus"]
                names = response.json()["names"]

                if self.last_num_users < self.num_users:
                    self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : f"{self.user_plus} вошел(а) в чат" })
                    self.last_num_users = self.num_users
                
                elif self.last_num_users > self.num_users:
                    self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : f"{self.user_minus} вышел(а) из чата" })
                    self.last_num_users = self.num_users

                for message in messages:
                    self.print_messages(message)
                    self.after = message["time"]

                if self.username not in names:
                    requests.get(f"http://{self.ip}:5000/plus_users", json={"user_plus" : self.username})
                    self.last_num_users += 1
                    self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : "Вы вошли в чат" })


            except:
                server_online = False
                self.pushButton_3.setVisible(True)
                return
        else:
            return

            
    def send_message(self):
        text = self.textEdit.toPlainText()

        try:
            if text.strip() == "":
                self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : "Проверьте сообщение" })

            else:
                if text == "/status":
                    self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : "Количество сообщений на сервере: " + str(self.num_messages) + "\nКоличество пользователей: " + str(self.num_users)})
                    self.textEdit.setText("")
                    return
                
                else:
                    requests.get(f"http://{self.ip}:5000/send_message", json={"username" : config["username"], "text" : text.strip()})

        except:
            self.print_messages({"username" : "Server", "time" : float(time.time()), "text" : "Сервер не доступен или введённый IP неправильный" })
            return

        self.textEdit.setText("")

#Scroll
stylesheet = """
QScrollBar:vertical
{
    background-color: rgb(255,255,255);
}

QScrollBar::handle:vertical
{
    background-color: rgb(230,230,230);         /* #605F5F; */
}

QScrollBar::handle:vertical:hover
{
    background-color: rgb(220,220,220);         /* #605F5F; */
}

"""


app = QtWidgets.QApplication([])
app.setStyleSheet(stylesheet)
window = Messanger()
window.show()
app.exec_()

try:
    if config["username"] != "" and config["username"] in names:
        requests.get(f"http://" + config["ip_server"] + ":5000/minus_users", json={"user_minus" : config["username"]})
    else:
        print("Имя отсутствует")
except:
    print("Сервер не доступен")