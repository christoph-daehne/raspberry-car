import { Direction } from "../Direction";
import { nats_publish_commands } from "../tauriApi";

export default class NatsClient {
    _direction = Direction.None;
    _lastPublish = Direction.None;
    _onDirectionChange?: (direction: Direction) => void;

    constructor() {
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
            await nats_publish_commands(this._direction);
            this._lastPublish = this._direction;
        }
    }
}
