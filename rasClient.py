
import socketio
import requests
r = requests.get('http://127.0.0.1:8000/test')
cl = socketio.Client()

tempHum = {
    "temp" :12,
    "humid": 25
}
@cl.on("control")
def control(data):
    print(f"command from user {data}")
cl.connect("http://127.0.0.1:8000/")
cl.emit("envi", tempHum)