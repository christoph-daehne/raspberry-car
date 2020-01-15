# Socket.IO Sample

## Getting started

### Server including Controller

```sh
nvm install
npm install -g yarn
yarn
yarn start
# download nipplejs.js into static/
# open http://localhost:3000/
```

### Emulated Car

```sh
python3 -m venv env
source env/bin/activate
pip install "python-socketio[client]"
python emulated-car.py
deactivate
```

## Raspberry Car

Replace the IP addresses and mind the firewall.

```sh
scp car.py pi@192.168.0.108:socket.io
ssh pi@192.168.0.108
python3 -m venv env
source env/bin/activate
pip install python-socketio[client]
pip install RPi.GPIO
python car.py http://192.168.0.106:3000
```
