import socketio

sio = socketio.Client()

@sio.event
def connect():
    print('connected to server')

@sio.event
def command(data):
    print('command: ', data)

@sio.event
def disconnect():
    print('disconnected from server')

sio.connect('http://localhost:3000')
sio.wait()
