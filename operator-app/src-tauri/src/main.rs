// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::env;
use std::thread;
use tauri::Manager;

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
    let nats_url = env::var("NATS_URL").unwrap_or("nats://localhost:4222".to_string());
    let creds_file = env::var("NATS_CREDS").unwrap_or("".to_string());
    if creds_file != "" {
        nats::Options::with_credentials(creds_file)
            .connect(nats_url)
            .expect("failed to connect to Nats")
    } else {
        nats::connect(nats_url).expect("failed to connect to Nats")
    }
}

fn nats_subscribe(nc: &nats::Connection, topic: &str) -> nats::Subscription {
    println!("Subscribing to {}", topic);
    // see https://docs.rs/nats/0.24.1/nats/struct.Subscription.html
    nc.subscribe(topic)
        .expect("Failed to subscribe to nats topic")
}

fn nats_message_to_string(msg: &nats::Message) -> String {
    std::str::from_utf8(&msg.data)
        .expect("Invalid UTF-8 sequence")
        .to_string()
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
    let nats_topic = env::var("NATS_TOPIC")
        .expect("expecting unset NATS_TOPIC, eg 'de.sandstorm.raspberry.car.1'");
    let commands_topic = nats_topic.clone() + ".commands";
    let all_topics = nats_topic + ".>";
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![console_log])
        .setup(move |app| {
            let nc = nats_connect();
            app.listen_global(
                "nats_publish__commands",
                move |event| match event_to_string(event.payload()) {
                    Some(payload) => {
                        nats_publish(&nc, &commands_topic, payload);
                    }
                    None => (),
                },
            );

            let handle = app.handle();

            // background worker to read nats events
            thread::spawn(move || {
                let nc = nats_connect();
                let sub = nats_subscribe(&nc, &all_topics);
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
