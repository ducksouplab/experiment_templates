(() => {
  var __defProp = Object.defineProperty;
  var __defProps = Object.defineProperties;
  var __getOwnPropDescs = Object.getOwnPropertyDescriptors;
  var __getOwnPropSymbols = Object.getOwnPropertySymbols;
  var __hasOwnProp = Object.prototype.hasOwnProperty;
  var __propIsEnum = Object.prototype.propertyIsEnumerable;
  var __defNormalProp = (obj, key, value) => key in obj ? __defProp(obj, key, { enumerable: true, configurable: true, writable: true, value }) : obj[key] = value;
  var __spreadValues = (a, b) => {
    for (var prop in b || (b = {}))
      if (__hasOwnProp.call(b, prop))
        __defNormalProp(a, prop, b[prop]);
    if (__getOwnPropSymbols)
      for (var prop of __getOwnPropSymbols(b)) {
        if (__propIsEnum.call(b, prop))
          __defNormalProp(a, prop, b[prop]);
      }
    return a;
  };
  var __spreadProps = (a, b) => __defProps(a, __getOwnPropDescs(b));

  // _front/src/social_contingency.js
  var state = {};
  var primaryToDucksoup = (kind, payload) => {
    if (!state.isPrimary)
      return;
    if (!state.ducksoup)
      return;
    state.ducksoup.send(kind, payload);
  };
  var showPlayer = () => {
    document.querySelector(".fixation-contents").classList.add("d-none");
    if (state.isSpeaker) {
      document.querySelector(".speaker-contents").classList.remove("d-none");
    }
    document.querySelector(".player-contents").classList.remove("d-none");
  };
  var replacePlayerMessage = (msg) => {
    document.querySelector("#ducksoup p").innerHTML = msg;
  };
  var init = async () => {
    const { fixationDuration, interactionDuration, isPrimary, isSpeaker, fromUserId, roundNumber } = js_vars;
    state.isPrimary = isPrimary;
    state.isSpeaker = isSpeaker;
    state.fromUserId = fromUserId;
    state.roundNumber = roundNumber;
    state.fixationDuration = fixationDuration;
    state.width = js_vars.peerOptions.width;
    state.height = js_vars.peerOptions.height;
    setTimeout(() => {
      showPlayer();
      primaryToDucksoup("round_start", state.roundNumber);
    }, fixationDuration * 1e3);
    replacePlayerMessage(fromUserId);
    const ducksoupPath = js_vars.playerOptions.ducksoupURL.split("://")[1];
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const embedOptions = __spreadProps(__spreadValues({}, js_vars.embedOptions), {
      callback: ducksoupListener
    });
    const peerOptions = __spreadProps(__spreadValues({}, js_vars.peerOptions), {
      duration: fixationDuration + interactionDuration,
      signalingUrl: "".concat(wsProtocol, "://").concat(ducksoupPath, "/ws"),
      logLevel: 2
    });
    window.ducksoup = await DuckSoup.render(embedOptions, peerOptions);
  };
  var ducksoupListener = ({ kind, payload }) => {
    if (kind === "other_joined") {
      if (payload.userId == state.fromUserId) {
        state.acceptStreamId = payload.streamId;
      }
      console.log("Accepts >>>", state.acceptStreamId);
    } else if (kind === "other_left") {
      if (payload.streamId == state.acceptStreamId) {
        delete state.acceptStreamId;
      }
    } else if (kind === "track") {
      const { track, streams } = payload;
      console.log("track from stream >>>", streams[0].id);
      if (streams[0].id !== state.acceptStreamId)
        return;
      if (state.isSpeaker && track.kind == "audio")
        return;
      console.log(track.kind + " track added");
      const oldEl = document.querySelector(".player-contents #ducksoup ".concat(track.kind));
      if (oldEl)
        oldEl.remove();
      const mountEl = document.getElementById("ducksoup");
      let el = document.createElement(track.kind);
      el.srcObject = streams[0];
      el.autoplay = true;
      el.muted = true;
      if (track.kind === "video") {
        el.style.width = state.width + "px";
        el.style.height = state.height + "px";
        mountEl.appendChild(el);
        console.log("appended", el);
        if (state.joinedType === "reconnection") {
          el.addEventListener("play", () => {
            showPlayer();
            primaryToDucksoup("round_start", state.roundNumber);
          });
        }
      } else if (track.kind === "audio") {
        mountEl.appendChild(el);
        if (state.joinedType === "reconnection") {
          el.addEventListener("play", () => {
            el.muted = false;
          });
        } else {
          setTimeout(() => {
            el.muted = false;
          }, state.fixationDuration * 1e3);
        }
      }
      streams[0].onremovetrack = ({ track: track2 }) => {
        const el2 = document.getElementById(track2.id);
        if (el2)
          el2.parentNode.removeChild(el2);
      };
    } else if (kind === "files" && payload) {
      document.querySelector(".speaker-contents").classList.add("d-none");
      document.querySelector(".player-contents").classList.add("d-none");
      const sanitizedPayload = {};
      const keys = Object.keys(payload);
      for (const key of keys) {
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
      if (!state.ended) {
        liveSend({
          kind: "visibility",
          payload: state.visibility
        });
        setTimeout(() => location.reload(), 5e3);
      }
    } else if (kind === "ending") {
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
})();
