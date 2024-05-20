(() => {
  // _front/src/brainstorm_detect_silence.js
  var state = {
    silentSteps: 0,
    speakingSteps: 0,
    playing: false
    // localStream
    // audioContext
    // micNode
  };
  var CONFIRM_SILENCE = 15;
  var CONFIRM_SPEAKING = 4;
  var THRESHOLD = 25;
  var ATTACK = 300;
  var RELEASE = 200;
  var ALPHA_SMILE = 0.8;
  var ALPHA_NEUTRAL = 0;
  var startSmile = () => {
    window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_SMILE, ATTACK, state.userId);
  };
  var stopSmile = () => {
    window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.userId);
  };
  var init = async () => {
    const { xpOptions: { videoFxName, userId, otherId } } = js_vars;
    state.videoFxName = videoFxName;
    state.userId = userId;
    state.otherId = otherId;
    state.audioContext = new AudioContext();
    await state.audioContext.audioWorklet.addModule("/static/global/lib/volume-meter.js");
    window.addPlayerListener((data) => {
      const { kind, payload } = data;
      if (kind == "local-stream") {
        state.localStream = payload;
      } else if (kind == "play" && !state.playing) {
        console.log("[brainstorm_ds] playing");
        state.playing = true;
        state.timeoutId = setTimeout(() => {
          processVolume(state.localStream);
        }, 2e3);
      } else if (kind == "end") {
        clearTimeout(state.timeoutId);
      }
    });
  };
  var processVolume = async (stream) => {
    const { audioContext, micNode } = state;
    if (micNode) {
      micNode.disconnect();
    }
    const sibling = document.querySelector(".help-container button");
    const volumeDisplay = document.createElement("div");
    volumeDisplay.classList.add("mt-2");
    volumeDisplay.classList.add("text-end");
    volumeDisplay.style.width = "86px";
    sibling.after(volumeDisplay);
    if (audioContext) {
      const micNode2 = audioContext.createMediaStreamSource(stream);
      state.micNode = micNode2;
      const volumeMeterNode = new AudioWorkletNode(audioContext, "volume-meter");
      volumeMeterNode.port.onmessage = ({ data }) => {
        const volume = data * 1e3;
        volumeDisplay.innerHTML = "".concat(Math.round(volume), " <> ").concat(THRESHOLD);
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
      micNode2.connect(volumeMeterNode).connect(audioContext.destination);
    }
  };
  document.addEventListener("DOMContentLoaded", init);
})();
