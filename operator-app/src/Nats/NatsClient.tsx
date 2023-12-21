import { Direction } from "../Direction";
import { nats_publish } from "../tauriApi";

const NATS_COMMANDS_TOPIC = "de.sandstorm.raspberry.car.1.commands";

export default class NatsClient {
    _direction = Direction.None;
    _lastPublish = Direction.None;
    _onDirectionChange?: (direction: Direction) => void;

    constructor() {
        /* does not work with vite
        (async () => {
            this._nc = await connect({ servers: "localhost" });

        })();*/
        setInterval(
            () => this._publishDirection(),
            1000
        );
    }

    async setDirection(direction: Direction) {
        this._direction = direction;
        await this._publishDirection();
    }

    async _publishDirection() {
        // only send 'None' once
        if (this._direction != Direction.None || this._lastPublish !== Direction.None) {
            // does not work with vite this._nc?.publish(NATS_COMMANDS_TOPIC, this._direction);
            await nats_publish("commands", this._direction);
            this._lastPublish = this._direction;
        }
    }
}
