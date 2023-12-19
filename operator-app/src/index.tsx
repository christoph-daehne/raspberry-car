/* @refresh reload */
import { render } from "solid-js/web";

import "./styles.css";
import App from "./App";
import { console_log } from "./tauriCommands";

const original_console_log = console.log;
console.log = async (...data: any[]) => {
    original_console_log(...data);
    console_log(...data);
}

console.log("Starting Operator App");
render(() => <App />, document.getElementById("root") as HTMLElement);
