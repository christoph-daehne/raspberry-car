import { createSignal, onCleanup, onMount } from "solid-js";
import "./App.css";
import VideoScreen from "./Components/VideoScreen/VideoScreen";
import Controls from "./Components/Controls/Controls";
import { Direction } from "./Direction";
import NatsClient from "./Nats/NatsClient";
import { UnlistenFn } from "@tauri-apps/api/event";
import { nats_subscribe } from "./tauriApi";

function App() {
  const natsClient = new NatsClient();
  const [activeDirection, setActiveDirection] = createSignal(Direction.None);

  let unsubscribe: UnlistenFn;
  onMount(async () => {
    unsubscribe = await nats_subscribe(
      "commands",
      (message: string) => {
        console.log('received direction', message);
        const direction = Direction[message as keyof typeof Direction]
        setActiveDirection(direction)
      }
    );
  });

  onCleanup(() => {
    if (unsubscribe) unsubscribe();
  })

  async function handleControlInput(direction: Direction) {
    console.log('sending direction', direction);
    setActiveDirection(direction);
    await natsClient.setDirection(direction);
  }

  async function handleKeyDown(e: KeyboardEvent) {
    console.log(e.key);
    // TODO: does not work
  }

  async function handleKeyUp(e: KeyboardEvent) {
    console.log(e.key);
    // TODO: does not work
  }

  return (
    <div class="container" onKeyDown={handleKeyDown} onKeyUp={handleKeyUp}>
      <h1>Raspberry Car 1</h1>
      <p>You can use W,A,S,D or the Arrow-Keys as well as the buttons</p>
      <Controls activeDirection={activeDirection} onChange={handleControlInput} />
      <div class="row my">
        <VideoScreen />
      </div>
    </div>
  );
}

export default App;
