const state = {
  silentSteps: 0,
  speakingSteps: 0,
  playing: false
  // localStream
  // audioContext
  // micNode
};

const CONFIRM_SILENCE = 15; // 16 x 40ms
const CONFIRM_SPEAKING = 4; // 5 x 40ms
const THRESHOLD = 25;
const ATTACK = 300;
const RELEASE = 200;
const ALPHA_SMILE = 0.8;
const ALPHA_NEUTRAL = 0;

const startSmile = () => {
  window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_SMILE, ATTACK, state.userId);
}

const stopSmile = () => {
  window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.userId);
}

const init = async () => {
  const { xpOptions: { videoFxName, userId, otherId} } = js_vars;
  state.videoFxName = videoFxName;
  state.userId = userId;
  state.otherId = otherId;

  state.audioContext = new AudioContext();
  await state.audioContext.audioWorklet.addModule('/static/global/lib/volume-meter.js');

  // callback from DuckSoup
  window.addPlayerListener((data) => {
    const { kind, payload } = data;
    if(kind == "local-stream") {
      state.localStream = payload;
    } else if(kind == "play" && !state.playing) {
      console.log("[brainstorm_ds] playing");
      state.playing = true;
      state.timeoutId = setTimeout(() => {
        processVolume(state.localStream);
      }, 2000); // wait 2s before starting processing
    } else if(kind == "end") {
      clearTimeout(state.timeoutId);
    } 
  });
};

const processVolume = async (stream) => {
  const { audioContext, micNode } = state;
  if (micNode) {
    micNode.disconnect();
  }
  // prepare debug display element
  const sibling = document.querySelector(".help-container button");
  const volumeDisplay = document.createElement("div");
  volumeDisplay.classList.add("mt-2");
  volumeDisplay.classList.add("text-end");
  volumeDisplay.style.width = "86px";

  sibling.after(volumeDisplay);

  // processing
  if (audioContext) {
    const micNode = audioContext.createMediaStreamSource(stream);
    state.micNode = micNode;
    const volumeMeterNode = new AudioWorkletNode(audioContext, 'volume-meter');
    
    volumeMeterNode.port.onmessage = ({data}) => {
      const volume = data * 1000;
      volumeDisplay.innerHTML = `${Math.round(volume)} <> ${THRESHOLD}`;
      if (volume < THRESHOLD) {
        if (state.silentSteps < CONFIRM_SILENCE) {
          state.silentSteps++;
          if (state.silentSteps == CONFIRM_SILENCE) {
            console.log("[brainstorm_ds] silence");
            startSmile();
            state.speakingSteps = 0;
          }
        } else if (state.speakingSteps < CONFIRM_SPEAKING) {
          state.speakingSteps = 0;
        }
      } else {
        if (state.speakingSteps < CONFIRM_SPEAKING) {
          state.speakingSteps++;
          if (state.speakingSteps == CONFIRM_SPEAKING) {
            console.log("[brainstorm_ds] speaking");
            stopSmile();
            state.silentSteps = 0;
          }
        } else if (state.silentSteps < CONFIRM_SILENCE) {
          state.silentSteps = 0;
        }
      }
    };
    micNode.connect(volumeMeterNode).connect(audioContext.destination);
  }
};

document.addEventListener("DOMContentLoaded", init);