from flask import Flask, request
import time


app = Flask(__name__)
messages = [ {"username": "Server", "text" : "FirstMessage", "time" : time.time()}]
names = []
num_users = 0
user_plus = ""
user_minus = ""
messenger_update = ""
clientui_update = ""
settingsui_update = ""

@app.route("/")
def Hello():
    return "Hello"

@app.route("/info")
def Info():
    return "This test server"

@app.route("/plus_users")
def plus_users():
    global num_users, user_plus, names
    num_users += 1
    user_plus = request.json["user_plus"]
    names.append(user_plus)
    return "User added successfully"

@app.route("/minus_users")
def minus_users():
    global num_users, user_minus
    num_users -= 1
    user_minus = request.json["user_minus"]
    names.remove(user_minus)
    return "User deleted successfully"

@app.route("/send_update")
def send_update():
    global messenger_update, clientui_update, settingsui_update
    messenger_update = request.json["messenger_update"]
    clientui_update  = request.json["clientui_update"]
    settingsui_update  = request.json["settingsui_update"]
    return "Update sent"
    
@app.route("/get_update")
def get_update():
    return {"messenger_update" : messenger_update, "clientui_update" : clientui_update, "settingsui_update" : settingsui_update}

@app.route("/send_message")
def send_message():
    username = request.json["username"]
    text = request.json["text"]

    messages.append({"username": username, "text" : text, "time" : float(time.time())})
    return 

@app.route("/get_messages")
def get_messages():
    after = float(request.args["after"])

    result = []

    for message in messages:
        if message["time"] > after:
            result.append(message)

    return{
        "messages": result,
        "num_messages" : len(messages),
        "num_users" : num_users,
        "user_plus" : user_plus,
        "user_minus" : user_minus,
        "names" : names
    }

app.run(host="192.168.157.1")