#!/bin/bash
############################## DEV_SCRIPT_MARKER ##############################
# This script is used to document and run recurring tasks in development.     #
#                                                                             #
# You can run your tasks using the script `./dev some-task`.                  #
# You can install the Sandstorm Dev Script Runner and run your tasks from any #
# nested folder using `dev some-task`.                                        #
# https://github.com/sandstorm/Sandstorm.DevScriptRunner                      #
###############################################################################

source ./dev_utilities.sh

set -e

NATS_TOPIC_PREFIX="de.sandstorm.raspberry.car.1"

######### TASKS #########

# Downloads and installs all dependencies
function setup() {
  _log_green "Installing required tools"
  which python3 || ( _log_red "Please install python3" && exit 1 )
  which bw || brew install bitwarden-cli
  which nats || brew install nats-io/nats-tools/nats
  which nats-server || brew install nats-server
  which cargo || brew install rust
  which fnm || brew install fnm
  # for the rust auto-formatter in VSCode
  which rustfmt || brew install rustfmt
  _log_green "Done"
}

# Start the entire local development stack
function up_local_dev() {
  setup
  up_nats_server
  up_operator
  up_car_emulator
}

# Terminates the entire local development stack
function down_local_dev() {
  down_nats_server
}

# Starts a local Nats.io server unless already running
function up_nats_server() {
  mkdir -p tmp
  nats publish "$NATS_TOPIC_PREFIX" "# ping" || nats-server \
    --name raspberry-car-dev-server \
    --pid ./tmp/nats-server.pid \
    > ./tmp/nats-server.log &
  sleep 1 # TODO: avoid timeout by checking for open port
}

# Terminates the local Nat.io server if running
function down_nats_server() {
  if [ -f "./tmp/nats-server.pid" ]; then
    kill $(cat ./tmp/nats-server.pid) || true
  fi
}

# Subscribes to the Raspberry Car message stream
function log_nats_messages() {
  nats subscribe "$NATS_TOPIC_PREFIX.>"
}

# Start the car emulator on the local machine.
function up_car_emulator() {
  up_nats_server
  # TODO: also emulate video stream
  log_nats_messages
}

# Start the operator client on the local machine.
function up_operator_app() {
  up_nats_server
  cd operator-app
  source <(fnm env)
  fnm install
  fnm use
  which yarn || npm install -g yarn
  yarn
  yarn tauri dev
}

# Publishes commands as if another operator would be using the same car
function fake_second_operator() {
  up_nats_server
  nats publish "$NATS_TOPIC_PREFIX.commands" "Left"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "Right"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "None"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "Foreward"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "Back"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "Left"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "Left"
  sleep 0.8
  nats publish "$NATS_TOPIC_PREFIX.commands" "None"
}

# Updates and start the daemon on the car.
function up_car() {
  _log_yellow "not yet implemented"
}

# Terminates the daemon on the car
function down_car() {
  _log_yellow "not yet implemented"
}

# Shuts down the Raspberry PI
function shutdown_car() {
  _log_yellow "not yet implemented"
}

_log_green "---------------------------- RUNNING TASK: $1 ----------------------------"

# THIS NEEDS TO BE LAST!!!
# this will run your tasks
"$@"
