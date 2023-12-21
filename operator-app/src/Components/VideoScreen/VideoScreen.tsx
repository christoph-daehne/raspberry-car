import { onCleanup, onMount } from "solid-js";
import "./VideoScreen.css";
import { nats_subscribe__images } from "../../tauriApi";
import { UnlistenFn } from "@tauri-apps/api/event";

function VideoScreen() {
  let image!: HTMLImageElement;

  let unsubscribe: UnlistenFn;
  onMount(async () => {
    // Video stream
    unsubscribe = await nats_subscribe__images(
      (uInt8Array: Uint8Array) => {
        // Kudos https://stackoverflow.com/questions/21434167/how-to-draw-an-image-on-canvas-from-a-byte-array-in-jpeg-or-png-format
        const binaryString = new Array<string>(uInt8Array.length);
        for (let i = 0; i <= uInt8Array.length; i++) {
          binaryString[i] = String.fromCharCode(uInt8Array[i]);
        }
        const data = binaryString.join('');
        const base64 = window.btoa(data);
        image.src = "data:image/jpg;base64," + base64;
      }
    );
  });
  onCleanup(() => {
    if (unsubscribe) unsubscribe();
  })

  return (
    <div>
      <img
        class="video-screen"
        width={320}
        height={256}
        ref={image}
        src=""
        alt="The video feed starts automatically when the car receives commands." />
      <p>The video feed starts automatically when the car receives commands.</p>
    </div>
  );
}

export default VideoScreen;
