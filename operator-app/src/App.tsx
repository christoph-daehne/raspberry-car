import { createSignal, onMount } from "solid-js";
import { invoke } from "@tauri-apps/api/tauri";
import "./App.css";

function App() {
  const [greetMsg, setGreetMsg] = createSignal("");
  const [name, setName] = createSignal("");

  async function greet() {
    // Learn more about Tauri commands at https://tauri.app/v1/guides/features/command
    setGreetMsg(await invoke("greet", { name: name() }));
  }

  let canvas!: HTMLCanvasElement;
  onMount(() => {
    const ctx = canvas.getContext("2d")!!;
    ctx.fillStyle = "#0f0f0f";
    ctx.font = '16px Avenir';
    ctx.textBaseline = 'middle';
    ctx.textAlign = "center";
    ctx.fillText(
      "The video feed starts automatically",
      (canvas.width / 2), 50);
    ctx.fillText(
      "while driving.",
      (canvas.width / 2), 68);
  });

  return (
    <div class="container">
      <h1>Raspberry Car 1</h1>
      <p>You can use W,A,S,D or the Arrow-Keys as well as the buttons</p>
      <div class="row">
        <button>Foreward</button>
      </div>
      <div class="row my">
        <button>Left</button>
        <button class="mx">Back</button>
        <button>Right</button>
      </div>
      <div class="row my">
        <canvas id="video" ref={canvas}></canvas>
      </div>
    </div>
  );
}

export default App;
