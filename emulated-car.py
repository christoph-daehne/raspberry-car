import socketio
import sys

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


if __name__ == '__main__':
    try:
        sio.connect(sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:3000')
        sio.wait()
    except KeyboardInterrupt:
        print('bye')
