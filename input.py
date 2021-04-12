import requests

username = input("Введите имя: ")
while True:
    text = input("Введите текст сообщения: ")

    if text == "":
        print("Сообщение не может быть пустым")
        continue

    requests.get("http://10.250.135.182:5000/send_message", json={"username" : username, "text" : text})