import { onMount } from "solid-js";
import "./VideoScreen.css";

function VideoScreen() {
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

  return <canvas id="video" ref={canvas}></canvas>;
}

export default VideoScreen;
