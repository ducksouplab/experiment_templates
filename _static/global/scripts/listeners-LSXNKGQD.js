(() => {
  // _front/src/listeners.js
  var state = {
    liveListeners: [],
    playerListeners: [],
    widthThresholdListeners: [],
    // width control
    currentWidth: 0,
    quality: void 0
  };
  window.addLiveListener = (cb) => {
    state.liveListeners = [...state.liveListeners, cb];
  };
  window.addPlayerListener = (cb) => {
    state.playerListeners = [...state.playerListeners, cb];
  };
  window.addWidthThresholdListener = (cb) => {
    if (typeof state.quality !== "undefined") {
      cb(state.quality);
    }
    state.widthThresholdListeners = [...state.widthThresholdListeners, cb];
  };
  window.liveRecv = (data) => {
    for (const cb of state.liveListeners) {
      cb(data);
    }
  };
  window.playerRecv = (data) => {
    for (const cb of state.playerListeners) {
      cb(data);
    }
  };
  var init = async () => {
    const { widthThreshold } = js_vars.listenerOptions;
    if (!widthThreshold)
      return;
    window.addPlayerListener((data) => {
      const { kind, payload } = data;
      if (kind === "stats" && payload.outboundRTPVideo && payload.outboundRTPVideo.frameWidth) {
        const newWidth = payload.outboundRTPVideo.frameWidth;
        if (state.currentWidth >= widthThreshold && newWidth < widthThreshold) {
          state.quality = false;
          state.currentWidth = newWidth;
          for (const cb of state.widthThresholdListeners) {
            cb(false);
          }
        } else if (state.currentWidth < widthThreshold && newWidth >= widthThreshold) {
          state.quality = true;
          state.currentWidth = newWidth;
          for (const cb of state.widthThresholdListeners) {
            cb(true);
          }
        }
      }
    });
  };
  document.addEventListener("DOMContentLoaded", init);
})();
