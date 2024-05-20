(() => {
  // _front/src/debug.js
  console.log("[Debug] v0.10.1");
  var state = {
    visibility: ""
  };
  var init = () => {
    document.getElementById("info").innerHTML = JSON.stringify({ js_vars }, null, 2);
    const mountEl = document.getElementById("ducksoup-root");
  };
  window.liveRecv = (data) => {
    if (data === "next") {
      setTimeout(() => {
        document.getElementById("form").submit();
      }, 2e3);
    }
  };
  document.addEventListener("DOMContentLoaded", init);
  document.addEventListener("visibilitychange", () => {
    state.visibility += "".concat((/* @__PURE__ */ new Date()).toLocaleTimeString(), "-> ").concat(document.visibilityState, " | ");
  });
})();
