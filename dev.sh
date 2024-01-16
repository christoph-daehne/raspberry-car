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

BALENA_FLEET="balena_cloud15/raspberry-car"
BALENA_DEVICE_CAR_1="46231ba"

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
  which gum || brew install gum
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
  pip3 install --requirement requirements.txt

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

# (Re)sets all environment variables in the balena fleet/device config
function balena_set_environment() {
  _log_yellow "Loading prodution settings"
  source ./profile.prod.sh

  _log_yellow "Settings env values"
  balena env add --fleet "$BALENA_FLEET" \
    NATS_URL "$NATS_URL"
  balena env add --fleet "$BALENA_FLEET" \
    NATS_CREDS "./de-sandstorm-raspberry-car-user.creds"
  balena env add --device "$BALENA_DEVICE_CAR_1" \
    NATS_TOPIC "$NATS_TOPIC"

  _log_green "Done"
  deploy_show_environment
}

# Shows the current configuration template in balena of Car 1
function balena_show_environment() {
  _log_yellow "Environment configuration of Car 1"
  balena envs --device "$BALENA_DEVICE_CAR_1" --json | jq .
}

# Builds and pushes the local version
function balena_release() {
  _balena_pre_build
  balena push "$BALENA_FLEET"
  _balena_post_build
}

# Rebuilds the local version and deploys it to the fleet
function balena_deploy() {
  _balena_pre_build
  balena deploy "$BALENA_FLEET" --build
  _balena_post_build
}

# Deploys the app directly to the Raspberry PI without creating a release
# This mode of local deployment hangs at the first INFO logs
# for > 10min. Since this is already an outragous round-trip time
# I stopped the deployment. However, I can connect via ssh.
function _balena_deploy_lan__does_not_work_but_hangs() {
  balena device local-mode "$BALENA_DEVICE_CAR_1" \
    | ack "Local mode on device $BALENA_DEVICE_CAR_1 is ENABLED" > /dev/null 2>&1 \
    || ( balena device local-mode "$BALENA_DEVICE_CAR_1" && exit 1 )
  local IP=$(balena device "$BALENA_DEVICE_CAR_1" --json | jq -r '.ip_address')
  _balena_pre_build
  _log_yellow "Pushing update directly to $IP"
  balena push "$IP"
  _balena_post_build
  _log_green "Done"
}

# Copies the local code into the target Raspberry cars running container via LAN via 'scp'.
# Note that this does **NOT** require the loca-mode to be enabled.
function balena_lan_deploy() {
  local IP=$(balena device "$BALENA_DEVICE_CAR_1" --json | jq -r '.ip_address')
  _log_yellow "Copying sources to $IP"
  # Since the root FS is read-only we must copy the source directly into the target container.
  local carContainer=$(ssh -p 22222 root@$IP \
      balena-engine ps --format '{{.Names}}' | ack 'car_')
  ( \
    cd car && \
    tar -c *.py raspberry/*.py \
      | ssh -p 22222 root@$IP \
          balena-engine cp - $carContainer:/app \
  )
  _log_green "Done"

  _log_yellow "Restarting Container"
  ssh -p 22222 root@$IP \
      balena-engine restart $carContainer
  _log_green "Done, boot might take a while, see 'dev balena_logs'"
}

function _balena_pre_build() {
  cp tmp/de-sandstorm-raspberry-car-user.creds car/de-sandstorm-raspberry-car-user.creds
}

function _balena_post_build() {
  rm car/de-sandstorm-raspberry-car-user.creds
}

# Opens a shell connection to the Raspberry PI
function balena_enter() {
  _log_green "You can mess around with 'balena-engine ps' and such."
  _log_yellow "!!! touch your YubiKey !!!"
  balena ssh "$BALENA_DEVICE_CAR_1"
}

# Shuts down the Raspbery PI "Car 1"
function balena_shutdown() {
  balena device shutdown "$BALENA_DEVICE_CAR_1"
}

# Shows the logs of the deployed services
function balena_logs() {
  balena logs "$BALENA_DEVICE_CAR_1" --tail
}

# Changes the WiFi settings on the connected SD card
function balena_add_wifi() {
  ls /Volumes/resin-boot/system-connections > /dev/null 2>&1 || ( _log_red "Please connect SD card, unable to locate /Volumes/resin-boot" && exit 1 )
  local ssid=${1:-$(gum input --placeholder="SSID")}
  local password=${2:-$(gum input --password --placeholder="password")}
  # see https://docs.balena.io/reference/OS/network/#wifi-setup
  local targetFile="/Volumes/resin-boot/system-connections/balena-$ssid-wifi"
  cat <<EOF > "$targetFile"
[connection]
id=$ssid-wifi
type=wifi

[wifi]
hidden=true
mode=infrastructure
ssid=$ssid
autoconnect-priority=10

[ipv4]
method=auto

[ipv6]
addr-gen-mode=stable-privacy
method=auto

[wifi-security]
auth-alg=open
key-mgmt=wpa-psk
psk=$password
EOF
  _log_green "Done, see $targetFile"
}

# Enables the Raspberry 3 camera modules and adjusts the GPU mem settings on the connected SD card
function balena_enable_camera_module() {
    local configPath="/Volumes/resin-boot/config.txt"
    ls "$configPath" > /dev/null 2>&1 || ( _log_red "Please connect SD card, unable to locate $configPath" && exit 1 )
    local configBlockMarker='## Raspberry Car configuration ##'
    if cat "$configPath" | ack "$configBlockMarker" > /dev/null 2>&1; then
      _log_green "$configPath already contains the Raspberry Car config block"
    else
      _log_yellow "Appending Raspberry Car config"
      cat <<EOF >> "$configPath"

#################################
$configBlockMarker
#################################
# Set to "1" to enable the camera module.
start_x=1
# GPU memory allocation in MB for 256MB board revision.
gpu_mem_256=192
# GPU memory allocation in MB for 512MB board revision.
gpu_mem_512=256
# GPU memory allocation in MB for 1024MB board revision.
gpu_mem_1024=448
EOF
      _log_green "Done"
    fi
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
