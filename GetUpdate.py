import requests

ip = input("Введите IP: ")

response = requests.get(f"http://{ip}:5000/get_update")

messenger_update = response.json()["messenger_update"]
clientui_update = response.json()["clientui_update"]

if messenger_update == "" and clientui_update == "":
    print("Отправте обновление")

else:
    file = open("messenger.py","w",encoding="utf-8")
    file.write(messenger_update)
    file.close()

    file = open("clientui.py","w",encoding="utf-8")
    file.write(clientui_update)
    file.close()
    print("Обновление загруженно")