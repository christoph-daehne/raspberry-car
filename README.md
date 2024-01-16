# Raspberry Car

A remote controlled car with a camera attached.
This rewrite uses Nats.io for communication between car and operator since
* our Nats.io infrastructure is in place
* it comes with authentication

## Tech Stack

* [Nats.io](https://nats.io/) for communication between car and client
* [Python](https://projects.raspberrypi.org/en/collections/python) on the car
    * [Python picamera](https://picamera.readthedocs.io/en/release-1.13/)
    * [Python Asyncio](https://realpython.com/async-io-python/)
* [balenaCloud](https://docs.balena.io/learn/getting-started/raspberrypi3/python/) for deployment to the car
    * [Raspberry-Car fleet](https://dashboard.balena-cloud.com/fleets/2104400)
    * [Device Setup](https://docs.balena.io/learn/getting-started/raspberrypi3/python/)
    * [Environment config](https://docs.balena.io/learn/manage/variables/)
    * [Balena CLI](https://docs.balena.io/reference/balena-cli/)
    * [Bundling](https://docs.balena.io/learn/develop/dockerfile/)
    * [WiFi Setup](https://docs.balena.io/reference/OS/network/#wifi-setup)
    * [balena-engine](https://engine-docs.balena.io/getting-started)
    * [Advanced boot settings](https://docs.balena.io/reference/OS/advanced/#raspberry-pi)
    * [Raspberry PI boot settings](https://www.raspberrypi.com/documentation/computers/config_txt.html)
    * [Balena Fleet Configuration](https://dashboard.balena-cloud.com/fleets/2104400/config)
* [Dev-Script-Runner](https://github.com/sandstorm/dev-script-runner) for custom dev-tools
    * [Bitwarden CLI](https://bitwarden.com/help/cli/)
    * [jq](https://jqlang.github.io/jq/)
    * [ack](https://beyondgrep.com/)
* [Tauri](https://tauri.app/) for the client desktop app
    * [Rust](https://www.rust-lang.org/) (for Tauri)
    * [Typescript](https://www.typescriptlang.org/)
    * [SolidJS](https://www.solidjs.com/)
    * [Yarn](https://yarnpkg.com/)
    * [Vite](https://vitejs.dev/)
    * [fnm](https://github.com/Schniz/fnm)

## Development Setup

### Recommended IDE Setup

* [VS Code](https://code.visualstudio.com/) + [Tauri](https://marketplace.visualstudio.com/items?itemName=tauri-apps.tauri-vscode)
* run `dev setup`

## Quick Start

You can work with the actual car or an emulated one.

1. (if working with real car) Place Raspberry Car in stand, such that wheel do not touch the ground.
2. (if working with real car) TODO: balena stuff
3. Now you can use the `dev` scripts.

* Code for the operator of the car resides in _operator-app_.
* Code for the car in _car_.

```shell
# local start
dev up_operator_app
dev up_car_emulator
…
dev down

# switch configuration profile
dev profile_local_activate           # Activates the configuration for a purely local development (default)
dev profile_sandstorm_nats_activate  # Activates the configuration using the prod Nats server for communication
dev profile_prod_activate            # Activates the production configuration using the real car with ID=1

# more commands
dev help

# enter Car 1
balena ssh 46231ba
```

## Technical background

The operator and car communicate voa Nats.io:
* server: [nats://localhost:4222]() for local dev, [tls://natsv1.cloud.sandstorm.de:32222]() for production
* topic: _de.sandstorm.raspberry.car.ID_ with _ID_ being the ID of the car

The operator sends commands to the car and the car sends its camera feed back.
