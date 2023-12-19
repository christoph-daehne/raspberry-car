import { invoke } from '@tauri-apps/api'
import { Direction } from './Direction';

export async function nats_publish(topic: string, direction: Direction) {
    await invoke(
        "nats_publish",
        { topic, message: String(direction) });
}

export async function console_log(...data: any[]) {
    const message = data
    .map(d => typeof d == "string" ? d : JSON.stringify(d))
    .join(" ");
    await invoke("console_log", { message });
}
