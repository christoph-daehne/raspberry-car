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

######### TASKS #########

# Downloads and installs all dependencies
function setup() {
  _log_green "Installing required tools"
  which python3 || ( _log_red "Please install python3" && exit 1 )
  which bw || brew install bitwarden-cli
  which jq || brew install jq
  which ack || brew install ack
  which nats || brew install nats-io/nats-tools/nats
  which nats-server || brew install nats-server
  which cargo || brew install rust
  which fnm || brew install fnm
  # for the rust auto-formatter in VSCode
  which rustfmt || brew install rustfmt
  _log_green "Done"
}

# Activates the configuration for a purely local development (default)
function profile_local_activate() {
  _profile_activate local
}

# Activates the configuration using the prod Nats server for communication
function profile_sandstorm_nats_activate() {
  _profile_activate sandstorm-nats
}

# Activates the production configuration using the real car with ID=1
function profile_prod_activate() {
  _profile_activate prod
}

function _profile_activate() {
  local profile=$1
  _log_yellow "Setting profile to '$profile'"
  cat "profile.$profile.sh" > profile.active.sh
  echo >> profile.active.sh
  fnm env >> profile.active.sh
  _log_green "Done"
}

# Start the entire local development stack
function up() {
  setup
  up_car_emulator
}

# Terminates the entire local development stack
function down() {
  down_nats_server
}

# Starts a local Nats.io server unless already running
function up_nats_server() {
  if echo $NATS_URL | ack localhost; then
    mkdir -p tmp
    nats publish "$NATS_TOPIC" "# ping" || nats-server \
      --name raspberry-car-dev-server \
      --pid ./tmp/nats-server.pid \
      > ./tmp/nats-server.log &
    sleep 1 # TODO: avoid timeout by checking for open port
  fi
}

# Terminates the local Nat.io server if running
function down_nats_server() {
  if [ -f "./tmp/nats-server.pid" ]; then
    kill $(cat ./tmp/nats-server.pid) || true
  fi
}

# Subscribes to the Raspberry Car message stream
function log_nats_messages() {
  nats subscribe "$NATS_TOPIC.>"
}

# Start the operator client on the local machine.
function up_operator_app() {
  up_nats_server
  cd operator-app
  # this only work in the terminal, not in this script source <(fnm env)
  fnm install
  fnm use
  which yarn || npm install -g yarn
  yarn
  _log_green "#######################################################"
  _log_green "# You might want to run 'dev up_car_emulator' as well #"
  _log_green "#######################################################"
  yarn tauri dev
}

# Starts the car service on the local machine without GPIO pins and camera
function up_car_emulator() {
  up_nats_server
  cd car
  _log_yellow "Setting up python project"
  ls venv || python3 -m venv venv
  source venv/bin/activate
  pip3 install --requirement requirements_emulator.txt

  _log_yellow "Starting emulator"
  CONTEXT=EMULATOR python3 main.py
}

# Publishes commands as if another operator would be using the same car.
function fake_second_operator() {
  up_nats_server
  while (true); do
    nats publish "$NATS_TOPIC.commands" "Left"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "Right"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "None"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "Foreward"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "Back"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "Left"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "Left"
    sleep 0.8
    nats publish "$NATS_TOPIC.commands" "None"
    sleep 0.8
  done;
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

if [ ! -f "./profile.active.sh" ]; then
  _log_green "activating default profile"
  profile_local_activate
fi
source ./profile.active.sh

# THIS NEEDS TO BE LAST!!!
# this will run your tasks
"$@"
