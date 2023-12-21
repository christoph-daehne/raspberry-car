import { invoke } from '@tauri-apps/api'
import { emit, listen } from '@tauri-apps/api/event'
import { Direction } from './Direction';

type PublishableTopics = "commands";
export async function nats_publish(topic: PublishableTopics, direction: Direction) {
    await emit(`nats_publish__${topic}`, direction);
}

export async function console_log(...data: any[]) {
    const message = data
        .map(d => typeof d === "string" ? d : JSON.stringify(d))
        .join(" ");
    await invoke("console_log", { message });
}

type NatsMessage = {
    message: string
}
export async function nats_subscribe__commands(callback: (message: string) => void) {
    return await listen<NatsMessage>(
        `nats_subscribe__commands`,
        (event) => callback(event.payload.message)
    );
}

type NatsBytes = {
    payload: Uint8Array
}
export async function nats_subscribe__images(callback: (payload: Uint8Array) => void) {
    return await listen<NatsBytes>(
        `nats_subscribe__images`,
        (event) => callback(event.payload.payload)
    );
}
