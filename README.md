# Raspberry Car

A remote controlled car with a camera attached.
This rewrite uses Nats.io for communication between car and operator since
* our Nats.io infrastructure is in place
* it comes with authentication

## Tech Stack

* [Nats.io](https://nats.io/)
* [Python on Raspberry PI](https://projects.raspberrypi.org/en/collections/python)
* [Debian Services](https://wiki.debian.org/systemd/Services)
* [Dev-Script-Runner](https://github.com/sandstorm/dev-script-runner)
* [Rust](https://www.rust-lang.org/) (for Tauri)
* [Tauri](https://tauri.app/)
* [SolidJS](https://www.solidjs.com/)
* [Typescript](https://www.typescriptlang.org/)
* [Yarn](https://yarnpkg.com/)
* [Vite](https://vitejs.dev/)
* [fnm](https://github.com/Schniz/fnm)

## Development Setup

### Recommended IDE Setup

* [VS Code](https://code.visualstudio.com/) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode) + [rust-analyzer](https://marketplace.visualstudio.com/items?itemName=rust-lang.rust-analyzer)
* run `dev setup`

## Quick Start

You can work with the actual car or an emulated one.

1. (if working with real car) Place Raspberry Car in stand, such that wheel do not touch the ground.
2. (if working with real car) Ensure WiFi car is connected to WiFi
3. (if working with real car) `export RASPBERRY_CAR_IP=<the IP address of the car>`
4. Now you can use the `dev` scripts.

* Code for the operator of the car resides in _operator-app_.
* Code for the car in _car_.
* _pre-natsio_ contains the code version prior to this re-write.

```shell
dev up_local_dev

# more commands
dev help
```

## Technical background

The operator and car communicate voa Nats.io:
* server: 
* topic: _de.sandstorm.raspberry.car.ID_ with _ID_ being the ID of the car

The operator sends commands to the car and the car sends its camera feed back.
