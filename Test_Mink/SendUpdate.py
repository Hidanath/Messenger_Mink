import requests

ip = input("Введите IP: ")

file = open("messenger.py","r",encoding="utf-8")
messenger_update = file.read()
file.close()

file = open("clientui.py","r",encoding="utf-8")
clientui_update = file.read()
file.close()

file = open("settingsui.py","r",encoding="utf-8")
settingsui_update = file.read()
file.close()

requests.get(f"http://{ip}:5000/send_update", json={"messenger_update" : messenger_update, "clientui_update" : clientui_update, "settingsui_update" : settingsui_update})

print("Обновление отправленно на сервер")