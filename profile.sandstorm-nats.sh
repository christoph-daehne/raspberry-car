_log_green "loading profile 'sandstorm-nats'"

export NATS_URL=tls://natsv1.cloud.sandstorm.de:32222
export NATS_CREDS=$(pwd)/tmp/de-sandstorm-raspberry-car-user.creds

if [ ! -f "$NATS_CREDS" ]; then
    _log_yellow "Missing Nats creds file at $NATS_CREDS, fetching it from Bitwarden"
    _log_yellow "You might need to provide your password"
    if test bw status 2> /dev/null | ack 'https://b1tw4rd3n.sandstorm.de' > /dev/null -ne 0; then
        echo "Setting Bitwarden server to https://b1tw4rd3n.sandstorm.de/"
        bw config server https://b1tw4rd3n.sandstorm.de/
        bw login
    fi
    bw sync
    mkdir -p tmp
    bw get attachment de-sandstorm-raspberry-car-user.creds \
        --itemid bdd21a6f-d0db-41f9-9842-25238252e892 \
        --output ./tmp/
fi

export NATS_TOPIC=de.sandstorm.raspberry.car.dev-$(echo $USER | sed -E 's/[^a-z]+//i')
