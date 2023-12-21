// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::thread;
use tauri::Manager;

const NATS_SERVER: &str = "localhost";

#[derive(Clone, serde::Serialize)]
struct NatsMessage {
    message: String,
}
#[derive(Clone, serde::Serialize)]
struct NatsBytes {
    payload: Vec<u8>,
}

#[tauri::command]
fn console_log(message: &str) {
    println!("ui: {}", message);
}

fn nats_connect() -> nats::Connection {
    return match nats::connect(NATS_SERVER) {
        Ok(nc) => nc,
        Err(error) => panic!("Failed to connect to nats: {:?}", error),
    };
}

fn nats_subscribe(nc: &nats::Connection, topic: &str) -> nats::Subscription {
    println!("Subscribing to {}", topic);
    // see https://docs.rs/nats/0.24.1/nats/struct.Subscription.html
    return match nc.subscribe(topic) {
        Ok(sub) => sub,
        Err(error) => panic!("Failed to subscribe to {:?}", error),
    };
}

fn nats_message_to_string(msg: &nats::Message) -> String {
    return match std::str::from_utf8(&msg.data) {
        Ok(v) => v.to_owned(),
        Err(e) => panic!("Invalid UTF-8 sequence: {}", e),
    };
}

fn nats_publish(nc: &nats::Connection, topic: &str, message: &str) {
    match nc.publish(topic, message) {
        Ok(_v) => (),
        Err(error) => println!("failed to send {} to {}: {}", message, topic, error),
    };
}

fn event_to_string(payload: Option<&str>) -> Option<&str> {
    // even string payloads are encoded as JSON
    return match payload {
        Some(json) => match serde_json::from_str(json) {
            Ok(v) => v,
            Err(_error) => None,
        },
        None => None,
    };
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![console_log])
        .setup(move |app| {
            let nc = nats_connect();
            app.listen_global(
                "nats_publish__commands",
                move |event| match event_to_string(event.payload()) {
                    Some(payload) => {
                        nats_publish(&nc, "de.sandstorm.raspberry.car.1.commands", payload);
                    }
                    None => (),
                },
            );

            let handle = app.handle();

            // background worker to read nats events
            thread::spawn(move || {
                let nc = nats_connect();
                let sub = nats_subscribe(&nc, "de.sandstorm.raspberry.car.1.>");
                loop {
                    if let Ok(msg) = sub.next_timeout(std::time::Duration::from_secs(300)) {
                        if msg.subject.ends_with(".commands") {
                            let message = nats_message_to_string(&msg);
                            handle
                                .emit_all(
                                    "nats_subscribe__commands",
                                    NatsMessage { message: message },
                                )
                                .unwrap();
                        }
                        if msg.subject.ends_with(".logs") {
                            println!("car: {}", nats_message_to_string(&msg));
                        }
                        if msg.subject.ends_with(".images") {
                            handle
                                .emit_all("nats_subscribe__images", NatsBytes { payload: msg.data })
                                .unwrap();
                        }
                    }
                }
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
