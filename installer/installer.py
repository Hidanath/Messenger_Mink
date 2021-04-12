import os 
command = input("Введите \"install\" чтобы установить mink: ")

messenger = '''from PyQt5 import QtWidgets, QtCore, QtGui
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

        new_ip = self.lineEdit_2.text().strip()
        new_username = self.lineEdit.text().strip()

        if new_username.strip() == "":
            self.textBrowser.setText("Имя не может быть пустым")
            return

        elif new_username in names:
            self.textBrowser.setText("Имя уже занято")
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

        new_ip = self.lineEdit_2.text().strip()
        new_username = self.lineEdit.text().strip()

        if new_username.strip() == "":
            self.textBrowser.setText("Имя не может быть пустым")
            return

        elif new_username in names:
            self.textBrowser.setText("Имя уже занято")
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
        """self.pushButton.setIcon(QtGui.QIcon(QtGui.QPixmap(os.getcwd() + "\\resourses\\Send.png")))
        self.pushButton.setIconSize(QtCore.QSize(32, 27))"""

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
                    if self.user_plus == self.username:
                        self.last_num_users = self.num_users

                    else:
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
    print("Сервер не доступен")'''

clientui = '''# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\MessangerUI.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(394, 460)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        MainWindow.setFont(font)
        MainWindow.setStyleSheet("background-color: rgb(62, 64, 85);")
        MainWindow.setIconSize(QtCore.QSize(24, 24))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(160, 5, 71, 31))
        font = QtGui.QFont()
        font.setFamily("Microsoft Sans Serif")
        font.setPointSize(25)
        font.setBold(False)
        font.setWeight(50)
        font.setKerning(True)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #fff;")
        self.label.setObjectName("label")
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(40, 400, 271, 32))
        self.textEdit.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;")
        self.textEdit.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.textEdit.setObjectName("textEdit")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(320, 400, 32, 32))
        font = QtGui.QFont()
        font.setPointSize(17)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("background-color: rgb(62, 64, 85);\n"
"border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;\n"
"padding-bottom: 3px;\n"
"padding-left: 0px;")
        self.pushButton.setObjectName("pushButton")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(40, 80, 312, 291))
        self.textBrowser.setAcceptDrops(True)
        self.textBrowser.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;")
        self.textBrowser.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAsNeeded)
        self.textBrowser.setSizeAdjustPolicy(QtWidgets.QAbstractScrollArea.AdjustIgnored)
        self.textBrowser.setMarkdown("")
        self.textBrowser.setObjectName("textBrowser")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(240, 50, 113, 23))
        self.lineEdit.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 7px;\n"
"color: #fff;\n"
"padding-left: 2px;\n"
"")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(40, 50, 113, 23))
        self.lineEdit_2.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 7px;\n"
"color: #fff;\n"
"padding-left: 2px;")
        self.lineEdit_2.setText("")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(265, 27, 65, 16))
        font = QtGui.QFont()
        font.setFamily("Microsoft Sans Serif")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: #fff;")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(75, 27, 41, 16))
        self.label_3.setStyleSheet("color: #fff;")
        self.label_3.setObjectName("label_3")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(180, 47, 31, 25))
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("border: none;\n"
"color: #fff;")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_3.setGeometry(QtCore.QRect(180, 85, 31, 38))
        font = QtGui.QFont()
        font.setPointSize(33)
        font.setBold(False)
        font.setWeight(50)
        self.pushButton_3.setFont(font)
        self.pushButton_3.setStyleSheet("border: none;\n"
"color: #FF6A5C;")
        self.pushButton_3.setObjectName("pushButton_3")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Mink"))
        self.label.setText(_translate("MainWindow", "Mink"))
        self.textEdit.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.textEdit.setPlaceholderText(_translate("MainWindow", "Введите сообщение..."))
        self.pushButton.setText(_translate("MainWindow", "➜"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.label_2.setText(_translate("MainWindow", "Ваше имя:"))
        self.label_3.setText(_translate("MainWindow", "Ваш IP:"))
        self.pushButton_2.setText(_translate("MainWindow", "☀"))
        self.pushButton_3.setText(_translate("MainWindow", "⟳"))
'''

settingsui = '''# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(394, 460)
        MainWindow.setStyleSheet("background-color:  rgb(62, 64, 85);")
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(126, 10, 142, 51))
        font = QtGui.QFont()
        font.setPointSize(30)
        self.label.setFont(font)
        self.label.setStyleSheet("color: #fff;")
        self.label.setObjectName("label")
        self.lineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit.setGeometry(QtCore.QRect(150, 90, 231, 32))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit.setFont(font)
        self.lineEdit.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;\n"
"padding-left: 4px;\n"
"padding-bottom: 2px;")
        self.lineEdit.setText("")
        self.lineEdit.setObjectName("lineEdit")
        self.lineEdit_2 = QtWidgets.QLineEdit(self.centralwidget)
        self.lineEdit_2.setGeometry(QtCore.QRect(150, 140, 231, 35))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;\n"
"padding-left: 4px;\n"
"padding-bottom: 2px;")
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(10, 132, 121, 41))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_2.setFont(font)
        self.label_2.setStyleSheet("color: #fff;")
        self.label_2.setObjectName("label_2")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(10, 86, 131, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.label_3.setFont(font)
        self.label_3.setStyleSheet("color: #fff;")
        self.label_3.setObjectName("label_3")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(10, 190, 371, 51))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.textBrowser.setFont(font)
        self.textBrowser.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 10px;\n"
"color: #fff;")
        self.textBrowser.setObjectName("textBrowser")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(10, 260, 371, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton.setFont(font)
        self.pushButton.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 20px;\n"
"background-color:  rgb(62, 64, 85);\n"
"color: #fff;")
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 330, 371, 51))
        font = QtGui.QFont()
        font.setPointSize(20)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setStyleSheet("border: 2px solid #FF6A5C;\n"
"border-radius: 20px;\n"
"background-color:  rgb(62, 64, 85);\n"
"color: #fff;")
        self.pushButton_2.setObjectName("pushButton_2")
        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Settings"))
        self.label.setText(_translate("MainWindow", "Settings"))
        self.label_2.setText(_translate("MainWindow", "IP адрес:"))
        self.label_3.setText(_translate("MainWindow", "Ваше имя:"))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:15pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Обновить"))
        self.pushButton_2.setText(_translate("MainWindow", "Сохранить"))
'''

if command == "install":
    with open("messenger.py", "w") as file:
        file.write(messenger)

    with open("settingsui.py", "w") as file:
        file.write(settingsui)

    with open("clientui.py", "w") as file:
        file.write(clientui)

    os.system("mkdir data")    
    os.system("mkdir resourses")
    os.system("cd resourses")
    

else:
    print("Комманда не верна")