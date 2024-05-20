const state = {
  liveListeners: [],
  playerListeners: [],
  widthThresholdListeners: [],
  // width control
  currentWidth: 0,
  quality: undefined,
}

window.addLiveListener = (cb) => {
  state.liveListeners = [...state.liveListeners, cb];
}

window.addPlayerListener = (cb) => {
  state.playerListeners = [...state.playerListeners, cb];
}

window.addWidthThresholdListener = (cb) => {
  if(typeof state.quality !== "undefined") { // instant feedback
    cb(state.quality);
  }
  state.widthThresholdListeners = [...state.widthThresholdListeners, cb];
}

window.liveRecv = (data) => {
  for(const cb of state.liveListeners) {
    cb(data);
  }
}

window.playerRecv = (data) => {
  for(const cb of state.playerListeners) {
    cb(data);
  }
}

const init = async () => {
  const { widthThreshold } = js_vars.listenerOptions;
  if(!widthThreshold) return;

  // callback from DuckSoup
  window.addPlayerListener((data) => {
    const { kind, payload } = data;

    if (kind === "stats" && payload.outboundRTPVideo && payload.outboundRTPVideo.frameWidth) {
      const newWidth = payload.outboundRTPVideo.frameWidth; // encoded width
      if(state.currentWidth >= widthThreshold && newWidth < widthThreshold) { // change
        state.quality = false;
        state.currentWidth = newWidth;
        for(const cb of state.widthThresholdListeners) {
          cb(false); // new quality went below threshod
        }
      } else if(state.currentWidth < widthThreshold && newWidth >= widthThreshold) { // other change
        state.quality = true;
        state.currentWidth = newWidth;
        for(const cb of state.widthThresholdListeners) {
          cb(true); // new quality went above threshod
        }
      } 
    }
  });
};

document.addEventListener("DOMContentLoaded", init);