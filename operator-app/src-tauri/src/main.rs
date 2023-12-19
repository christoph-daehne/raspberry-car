// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

static mut NATS_CONNECTION: Option<nats::Connection> = None;
const NATS_TOPIC: &str = "de.sandstorm.raspberry.car.1";
const NATS_SERVER: &str = "localhost";

#[tauri::command]
fn console_log(message: &str) {
    println!("console.log({})", message);
}

#[tauri::command]
fn nats_publish(topic: &str, message: &str) {
    unsafe {
        match &NATS_CONNECTION {
            Some(nc) => match nc.publish(&(NATS_TOPIC.to_owned() + "." + topic), message) {
                Ok(_v) => (),
                Err(error) => println!("failed to send {} to {}: {}", message, topic, error),
            },
            None => println!(
                "Not connected to Nats: cannot sent {} to {}",
                message, topic
            ),
        }
    }
}

fn nats_connect() {
    unsafe {
        NATS_CONNECTION = Some(match nats::connect(NATS_SERVER) {
            Ok(nc) => nc,
            Err(error) => panic!("Failed to connect to nats: {:?}", error),
        });
    }
}

fn main() {
    nats_connect();
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![nats_publish, console_log])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
