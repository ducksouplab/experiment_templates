const state = {};

const primaryToDucksoup = (kind, payload) => {
  if (!state.isPrimary) return;
  if (!state.ducksoup) return;
  state.ducksoup.send(kind, payload);
}

const showPlayer = () => {
  document.querySelector(".fixation-contents").classList.add("d-none");
  if (state.isSpeaker) {
    document.querySelector(".speaker-contents").classList.remove("d-none");
  }
  document.querySelector(".player-contents").classList.remove("d-none");
}

const replacePlayerMessage = (msg) => {
  document.querySelector("#ducksoup p").innerHTML = msg;
}

const init = async () => {
  const { fixationDuration, interactionDuration, isPrimary, isSpeaker, fromUserId, roundNumber } = js_vars;
  // console.log(js_vars);

  state.isPrimary = isPrimary;
  state.isSpeaker = isSpeaker;
  state.fromUserId = fromUserId;
  state.roundNumber = roundNumber;
  state.fixationDuration = fixationDuration;
  state.width = js_vars.peerOptions.width;
  state.height = js_vars.peerOptions.height;

  // UX
  setTimeout(() => {
    showPlayer();
    primaryToDucksoup("round_start", state.roundNumber);
  }, fixationDuration * 1000);
  replacePlayerMessage(fromUserId);

  // DuckSoup player
  const ducksoupPath = js_vars.playerOptions.ducksoupURL.split("://")[1];
  const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";

  const embedOptions = {
    ...js_vars.embedOptions,
    callback: ducksoupListener,
  }
  const peerOptions = {
    ...js_vars.peerOptions,
    duration: fixationDuration + interactionDuration,
    signalingUrl: `${wsProtocol}://${ducksoupPath}/ws`,
    logLevel: 2
  };

  window.ducksoup = await DuckSoup.render(embedOptions, peerOptions);
};

// callback triggered by DuckSoup player
const ducksoupListener = ({ kind, payload }) => {
  if (kind === "other_joined") {
    if (payload.userId == state.fromUserId) {
      state.acceptStreamId = payload.streamId;
    }
    console.log("Accepts >>>", state.acceptStreamId);
  } else if (kind === "other_left") {
    if (payload.streamId == state.acceptStreamId) {
      delete(state.acceptStreamId); 
    }
  } else if (kind === "track") {
    const { track, streams } = payload;
    console.log("track from stream >>>", streams[0].id);
    if (streams[0].id !== state.acceptStreamId) return; // only reveal a given stream
    if (state.isSpeaker && track.kind == "audio") return; // speakers don't listen
    console.log(track.kind + " track added");

    // cleanup
    const oldEl = document.querySelector(`.player-contents #ducksoup ${track.kind}`);
    if (oldEl) oldEl.remove();
    // mount new one
    const mountEl = document.getElementById("ducksoup");
    // create <video> or <audio>
    let el = document.createElement(track.kind);
    el.srcObject = streams[0];
    el.autoplay = true;
    el.muted = true;
    if (track.kind === "video") {
      // size
      el.style.width = state.width + "px";
      el.style.height = state.height + "px";
      // append
      mountEl.appendChild(el);
      console.log("appended", el)
      // show
      if (state.joinedType === "reconnection") {
        // when it's a reconnection we don't want to wait for fixation to end
        el.addEventListener("play", () => {
          showPlayer();
          primaryToDucksoup("round_start", state.roundNumber);
        });
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
        }, state.fixationDuration * 1000);
      }
    }
    // on remove
    streams[0].onremovetrack = ({ track }) => {
      const el = document.getElementById(track.id);
      if (el) el.parentNode.removeChild(el);
    };
  } else if (kind === "files" && payload) {
    document.querySelector(".speaker-contents").classList.add("d-none");
    document.querySelector(".player-contents").classList.add("d-none");
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
    // TODO? show ending message
  } else if (kind === "error-full") {
    replacePlayerMessage("Error: room is full");
  } else if (kind === "error-duplicate") {
    replacePlayerMessage("Error: already connected");
  } else if (kind === "error") {
    replacePlayerMessage("Error");
  } else if (kind === "joined") {
    state.joinedType = payload;
  }
};

document.addEventListener("DOMContentLoaded", init);

window.addEventListener("beforeunload", () => {
  window.ducksoup && window.ducksoup.stop();
});