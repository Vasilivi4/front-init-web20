from flask import Flask, render_template, request, send_from_directory
from flask_socketio import SocketIO
from datetime import datetime
import socket
import json
import os
import threading

app = Flask(__name__, template_folder="templates")
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/message", methods=["GET", "POST"])
def message():
    if request.method == "POST":
        username = request.form.get("username")
        message_text = request.form.get("message")

        if not username or not message_text:
            return render_template(
                "error.html", error="Username and message are required."
            )

        message_data = {"username": username, "message": message_text}
        socketio.emit("new_message", message_data)

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
        with open("storage/data.json", "a") as f:
            json.dump([{timestamp: message_data}], f, indent=2)
            f.write(",\n")

        return render_template("message.html", username=username, message=message_text)
    else:
        return render_template("message.html")


@app.route("/static/<path:filename>")
def serve_static(filename):
    return send_from_directory("front-init", "static/" + filename)


@socketio.on("connect")
def handle_connect():
    print("Client connected")


def handle_client(client_socket):
    data = client_socket.recv(1024)
    data_dict = json.loads(data.decode("utf-8"))

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    with open("storage/data.json", "a") as f:
        json.dump({timestamp: data_dict}, f, indent=2)
        f.write(",\n")

    client_socket.close()


def start_socket_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind(("0.0.0.0", 5000))

    print("Socket server started")

    while True:
        data, addr = server.recvfrom(1024)
        client_thread = threading.Thread(target=handle_client, args=(data,))
        client_thread.start()


if __name__ == "__main__":
    storage_path = "storage"

    if not os.path.exists(storage_path):
        os.makedirs(storage_path)

    data_file = os.path.join(storage_path, "data.json")

    if not os.path.exists(data_file):
        with open(data_file, "w") as f:
            f.write("[]")

    threading.Thread(target=start_socket_server).start()
    socketio.run(app, port=3000)
