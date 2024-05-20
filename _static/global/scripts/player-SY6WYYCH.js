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

  // _front/src/player.js
  console.log("[Interact] v1.1.3");
  var state = {
    visibility: "",
    ended: false
    // peerOptions
    // embedOptions
    // joinedType
  };
  var WIDTH_OVERRIDE = 800;
  var HEIGHT_OVERRIDE = 600;
  var init = async () => {
    const { playerOptions, connectingDuration, interactionDuration } = js_vars;
    state.connectingDuration = connectingDuration * 1e3;
    const ducksoupPath = playerOptions.ducksoupURL.split("://")[1];
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const embedOptions = __spreadProps(__spreadValues({}, js_vars.embedOptions), {
      callback: ducksoupListener
    });
    const peerOptions = __spreadProps(__spreadValues({}, js_vars.peerOptions), {
      duration: connectingDuration + interactionDuration,
      signalingUrl: "".concat(wsProtocol, "://").concat(ducksoupPath, "/ws"),
      logLevel: 2
    });
    window.ducksoup = await DuckSoup.render(embedOptions, peerOptions);
    state.peerOptions = peerOptions;
    window.addLiveListener((data) => {
      const { kind } = data;
      if (kind === "next") {
        setTimeout(() => {
          document.getElementById("form").submit();
        }, 2e3);
      }
    });
  };
  var hideDuckSoup = () => {
    document.getElementById("stopped").classList.remove("d-none");
    document.getElementById("ducksoup-root").classList.add("d-none");
  };
  var replaceMessage = (message) => {
    document.getElementById("stopped-message").innerHTML = message;
    hideDuckSoup();
  };
  var ducksoupListener = (message) => {
    const { kind, payload } = message;
    if (kind === "track") {
      const { track, streams } = payload;
      console.log("[From Ducksoup] track kind: " + track.kind);
      const oldEl = document.querySelector("#ducksoup-root ".concat(track.kind));
      if (oldEl)
        oldEl.remove();
      const mountEl = document.getElementById("ducksoup-root");
      let el = document.createElement(track.kind);
      el.srcObject = streams[0];
      el.autoplay = true;
      el.muted = true;
      if (track.kind === "video") {
        el.style.width = WIDTH_OVERRIDE + "px";
        el.style.height = HEIGHT_OVERRIDE + "px";
        mountEl.appendChild(el);
        if (state.joinedType === "reconnection") {
          el.addEventListener("play", () => {
            window.playerRecv({ kind: "play" });
            document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
          });
        } else {
          setTimeout(() => {
            console.log("[Interact] show video");
            window.playerRecv({ kind: "play" });
            document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
            document.querySelector(".ducksoup-container #ducksoup-root").classList.remove("d-none");
          }, state.connectingDuration);
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
          }, state.connectingDuration);
        }
      }
      streams[0].onremovetrack = ({ track: track2 }) => {
        const el2 = document.getElementById(track2.id);
        if (el2)
          el2.parentNode.removeChild(el2);
      };
    } else if (kind === "files" && payload) {
      document.querySelector(".ducksoup-container").classList.add("d-none");
      document.querySelector(".help-container").classList.add("d-none");
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
      document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
      document.querySelector(".ducksoup-container .ending").classList.remove("d-none");
    } else if (kind === "error-full") {
      replaceMessage("Connexion refus\xE9e (salle compl\xE8te)");
    } else if (kind === "error-duplicate") {
      replaceMessage("Connexion refus\xE9e (d\xE9j\xE0 connect\xE9-e)");
    } else if (kind === "error") {
      replaceMessage("Erreur");
    } else if (kind === "joined") {
      state.joinedType = payload;
      document.querySelector(".ducksoup-container .connecting").classList.remove("d-none");
      if (payload === "reconnection") {
        document.querySelector(".ducksoup-container #ducksoup-root").classList.remove("d-none");
      }
    }
    window.playerRecv(message);
  };
  document.addEventListener("DOMContentLoaded", init);
  window.addEventListener("beforeunload", () => {
    window.ducksoup && window.ducksoup.stop();
  });
  document.addEventListener("visibilitychange", () => {
    state.visibility += "".concat((/* @__PURE__ */ new Date()).toLocaleTimeString(), "-> ").concat(document.visibilityState, " | ");
  });
})();
