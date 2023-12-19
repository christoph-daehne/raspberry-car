import { Direction } from "../Direction";
import { nats_publish } from "../tauriCommands";

export default class NatsClient {
    _direction = Direction.None;
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
        await nats_publish("commands", this._direction);
    }
}
