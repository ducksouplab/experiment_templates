console.log("[Interact] v1.1.3");

const state = {
  visibility: "",
  ended: false,
  // peerOptions
  // embedOptions
  // joinedType
};

const WIDTH_OVERRIDE = 800;
const HEIGHT_OVERRIDE = 600;

const init = async () => {
  const { playerOptions, connectingDuration, interactionDuration } = js_vars;
  state.connectingDuration = connectingDuration * 1000; // seconds to ms
  
  // DuckSoup player
  const ducksoupPath = playerOptions.ducksoupURL.split("://")[1];
  const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";

  const embedOptions = {
    ...js_vars.embedOptions,
    callback: ducksoupListener,
  }
  const peerOptions = {
    ...js_vars.peerOptions,
    duration: connectingDuration + interactionDuration,
    signalingUrl: `${wsProtocol}://${ducksoupPath}/ws`,
    logLevel: 2
  };

  window.ducksoup = await DuckSoup.render(embedOptions, peerOptions);
  state.peerOptions = peerOptions;
  
  // callback from python
  window.addLiveListener((data) => {
    const { kind } = data;
    if(kind === 'next') {   
      setTimeout(() => {
        document.getElementById("form").submit();
      }, 2000);
    }
  });
};

const hideDuckSoup = () => {
  document.getElementById("stopped").classList.remove("d-none");
  document.getElementById("ducksoup-root").classList.add("d-none");
}

const replaceMessage = (message) => {
  document.getElementById("stopped-message").innerHTML = message;
  hideDuckSoup();
}

// callback triggered by DuckSoup player
const ducksoupListener = (message) => {
  const { kind, payload } = message;

  if (kind === "track") {
    const { track, streams } = payload;
    console.log("[From Ducksoup] track kind: " + track.kind);
    // cleanup
    const oldEl = document.querySelector(`#ducksoup-root ${track.kind}`);
    if (oldEl) oldEl.remove();
    // mount new one
    const mountEl = document.getElementById("ducksoup-root");
    // create <video> or <audio>
    let el = document.createElement(track.kind);
    el.srcObject = streams[0];
    el.autoplay = true;
    el.muted = true;
    if (track.kind === "video") {
      // size
      el.style.width = WIDTH_OVERRIDE + "px";// state.peerOptions.width + "px";
      el.style.height = HEIGHT_OVERRIDE + "px";//state.peerOptions.height + "px";
      // append
      mountEl.appendChild(el);
      // show
      if (state.joinedType === "reconnection") {
        // when it's a reconnection we don't want to wait for connectingDuration
        // we'd rather show the video as soon as it's playing
        el.addEventListener("play", () => {
          window.playerRecv({ kind: "play" });
          document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
        });
      } else {
        // we wait for connectionDuration, to avoid instabilities and quality problems
        // that are common during the first seconds
        setTimeout(() => {
            console.log("[Interact] show video");
            window.playerRecv({ kind: "play" });
            document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
            document.querySelector(".ducksoup-container #ducksoup-root").classList.remove("d-none");
        }, state.connectingDuration);
      }
    } else if (track.kind === "audio") {
      // append
      mountEl.appendChild(el);
      // unmute
      if (state.joinedType === "reconnection") {
        el.addEventListener("play", () => {
          el.muted = false;
        });
      } else {
        setTimeout(() => {
            el.muted = false;
        }, state.connectingDuration);
      }
    }
    // on remove
    streams[0].onremovetrack = ({ track }) => {
      const el = document.getElementById(track.id);
      if (el) el.parentNode.removeChild(el);
    };
  } else if (kind === "files" && payload) {
    document.querySelector(".ducksoup-container").classList.add("d-none");
    document.querySelector(".help-container").classList.add("d-none");
    const sanitizedPayload = {};
    const keys = Object.keys(payload);
    for(const key of keys) {
      sanitizedPayload[key] = payload[key].join(";");
    }
    liveSend({
      kind: "files",
      payload: sanitizedPayload
    });
  } else if (kind === "end") {
    state.ended = true;
    liveSend({
      kind: "end"
    });
  } else if (kind === "closed") {
    // caution: "closed" may happen when room has ended server side
    // > OR if there is a server or connection error
    if(!state.ended) {
      liveSend({
        kind: "visibility",
        payload: state.visibility
      });
      setTimeout(() => location.reload(), 5000);
    }
  } else if (kind === "ending") {
    document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
    document.querySelector(".ducksoup-container .ending").classList.remove("d-none");
  } else if (kind === "error-full") {
    replaceMessage("Connexion refusée (salle complète)");
  } else if (kind === "error-duplicate") {
    replaceMessage("Connexion refusée (déjà connecté-e)");
  } else if (kind === "error") {
    replaceMessage("Erreur");
  } else if (kind === "joined") {
    state.joinedType = payload;
    document.querySelector(".ducksoup-container .connecting").classList.remove("d-none");
    if (payload === "reconnection") {
      document.querySelector(".ducksoup-container #ducksoup-root").classList.remove("d-none");
    }
  } 
  // send to other listeners
  window.playerRecv(message);
};

document.addEventListener("DOMContentLoaded", init);

window.addEventListener("beforeunload", () => {
  window.ducksoup && window.ducksoup.stop();
});

document.addEventListener('visibilitychange', () => {
  state.visibility += `${(new Date()).toLocaleTimeString()}-> ${document.visibilityState} | `;
});