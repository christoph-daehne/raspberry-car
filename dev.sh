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
  which nats || brew install nats-io/nats-tools/nats
  _log_green "Done"
}

# Start the car emulator on the local machine.
function up_emulator() {
  _log_yellow "not yet implemented"
}

# Start the operator client on the local machine.
function up_operator() {
  _log_yellow "not yet implemented"
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
