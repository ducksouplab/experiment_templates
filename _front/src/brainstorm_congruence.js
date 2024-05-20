// DRAFT just to showcase communication between primary and secondary

const state = {
  silentSteps: 0,
  primaryUnderFX: false,
  secondaryUnderFX: false,
  // primary
  // audioContext
  // micNode
};

const CONFIRM_SILENCE = 11; // 12 x 40ms
const ATTACK = 300;
const RELEASE = 200;
const ALPHA_SMILE = 0.8;
const ALPHA_NEUTRAL = 0;


const startSmile = (id) => {
  window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_SMILE, ATTACK, id);
}

const stopSmile = (id) => {
  window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, id);
}

const init = async () => {
  const { xpOptions: { primary, videoFxName, userId, otherId} } = js_vars;
  state.primary = !!primary;
  state.videoFxName = videoFxName;
  state.userId = userId;
  state.otherId = otherId;

  state.audioContext = new AudioContext();
  await state.audioContext.audioWorklet.addModule('/static/global/lib/volume-meter.js');
 
  // callback from python
  window.addLiveListener((data) => {
    const { kind } = data;
    if(kind == "from-secondary") {
      console.log(data);
    } 
  });

  // callback from DuckSoup
  window.addPlayerListener((data) => {
    const { kind, payload } = data;
    if(kind == "local-stream") {
      processVolume(payload);
    } 
  });
};

const processVolume = async (stream) => {
  const { audioContext, micNode } = state;
  if (micNode) {
    micNode.disconnect();
  }
  if (audioContext) {
    const micNode = audioContext.createMediaStreamSource(stream);
    state.micNode = micNode;
    const volumeMeterNode = new AudioWorkletNode(audioContext, 'volume-meter');   
    volumeMeterNode.port.onmessage = ({data}) => {
      const volume = data * 1000;
      if (volume < 10) {
        if (state.silentSteps < CONFIRM_SILENCE) {
          state.silentSteps++;
          if (state.silentSteps == CONFIRM_SILENCE) {
            if (state.primary) {
              console.log("primary silent");
            } else {
              console.log("secondary silent");
              liveSend({kind: "to-primary", payload: "silent"});
            }
          }
        }
      } else if (state.silentSteps != 0) {
        if (state.silentSteps == CONFIRM_SILENCE) {
          if (state.primary) {
            console.log("primary speaking");
          } else {
            console.log("secondary speaking");
            liveSend({kind: "to-primary", payload: "speaking"});
          }
        }
        state.silentSteps = 0;
      }
    };
    micNode.connect(volumeMeterNode).connect(audioContext.destination);
  }
};

document.addEventListener("DOMContentLoaded", init);