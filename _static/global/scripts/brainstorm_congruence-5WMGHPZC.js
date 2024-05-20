(() => {
  // _front/src/brainstorm_congruence.js
  var state = {
    silentSteps: 0,
    primaryUnderFX: false,
    secondaryUnderFX: false
    // primary
    // audioContext
    // micNode
  };
  var CONFIRM_SILENCE = 11;
  var init = async () => {
    const { xpOptions: { primary, videoFxName, userId, otherId } } = js_vars;
    state.primary = !!primary;
    state.videoFxName = videoFxName;
    state.userId = userId;
    state.otherId = otherId;
    state.audioContext = new AudioContext();
    await state.audioContext.audioWorklet.addModule("/static/global/lib/volume-meter.js");
    window.addLiveListener((data) => {
      const { kind } = data;
      if (kind == "from-secondary") {
        console.log(data);
      }
    });
    window.addPlayerListener((data) => {
      const { kind, payload } = data;
      if (kind == "local-stream") {
        processVolume(payload);
      }
    });
  };
  var processVolume = async (stream) => {
    const { audioContext, micNode } = state;
    if (micNode) {
      micNode.disconnect();
    }
    if (audioContext) {
      const micNode2 = audioContext.createMediaStreamSource(stream);
      state.micNode = micNode2;
      const volumeMeterNode = new AudioWorkletNode(audioContext, "volume-meter");
      volumeMeterNode.port.onmessage = ({ data }) => {
        const volume = data * 1e3;
        if (volume < 10) {
          if (state.silentSteps < CONFIRM_SILENCE) {
            state.silentSteps++;
            if (state.silentSteps == CONFIRM_SILENCE) {
              if (state.primary) {
                console.log("primary silent");
              } else {
                console.log("secondary silent");
                liveSend({ kind: "to-primary", payload: "silent" });
              }
            }
          }
        } else if (state.silentSteps != 0) {
          if (state.silentSteps == CONFIRM_SILENCE) {
            if (state.primary) {
              console.log("primary speaking");
            } else {
              console.log("secondary speaking");
              liveSend({ kind: "to-primary", payload: "speaking" });
            }
          }
          state.silentSteps = 0;
        }
      };
      micNode2.connect(volumeMeterNode).connect(audioContext.destination);
    }
  };
  document.addEventListener("DOMContentLoaded", init);
})();
