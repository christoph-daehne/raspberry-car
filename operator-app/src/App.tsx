import { createSignal, onMount } from "solid-js";
import "./App.css";
import VideoScreen from "./Components/VideoScreen/VideoScreen";
import Controls from "./Components/Controls/Controls";
import { Direction } from "./Direction";
import NatsClient from "./Nats/NatsClient";


function App() {
  const natsClient = new NatsClient();
  const [activeDirection, setActiveDirection] = createSignal(Direction.None);

  async function handleControlInput(direction: Direction) {
    console.log({ direction });
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
      <Controls activeDirection={activeDirection()} onChange={handleControlInput} />
      <div class="row my">
        <VideoScreen />
      </div>
    </div>
  );
}

export default App;
