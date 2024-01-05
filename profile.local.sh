_log_green "loading profile 'local'"

export NATS_URL=nats://localhost:4222
unset NATS_CREDS
export NATS_TOPIC=de.sandstorm.raspberry.car.dev-$(echo $USER | sed -E 's/[^a-z]+//i')
