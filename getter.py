import requests
import time
import datetime

lastTimeStamp = 0.0

while True:
    response = requests.get("http://10.250.135.182:5000/get_messages", params={"after" : lastTimeStamp})
    messages = response.json()["messages"]
    for message in messages:
        dt = datetime.datetime.fromtimestamp(message["time"])
        dt = dt.strftime("%H:%M:%S %d/%m/%Y")
        print(message["username"], dt)
        print(message["text"] + "\n")

        lastTimeStamp = message["time"]

    time.sleep(1.0)