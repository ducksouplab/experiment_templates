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
  console.log("hideDucksoup");
}

const replaceMessage = (message) => {
  document.getElementById("stopped-message").innerHTML = message;
  hideDuckSoup();
  console.log("replaceMessage");
}

//######################################################//
//## SETUP TO MONITOR VOLUME LEVELS DURING AUDIO TEST //##
//######################################################//
// Activate logging
let timeoutId;
let volumeLevels = []; // Array to store volume levels
let noiseLevels = []; // Array to store noise levels
let volumeLoggingActive = false; // Flag to track logging state
let currentPhase = "noise"
let analyser, audioContext, dataArray;

 // Log volume level
 function logVolumeLevel() {
  if (!volumeLoggingActive) return; // Stop logging if the flag is false
  analyser.getByteFrequencyData(dataArray);
  var volume = dataArray.reduce((a, b) => a + b, 0) / dataArray.length;
  // Store the noise level
  if (currentPhase == "noise"){noiseLevels.push(volume);}
  // Store the volume level
  if (currentPhase == "signal"){volumeLevels.push(volume);}
  // Continue logging
  requestAnimationFrame(logVolumeLevel);
}

// Helper function to calculate median
function calculateMedian(arr) {
  if (arr.length === 0) return 0; // Handle empty array case

  const sortedArr = [...arr].sort((a, b) => a - b);
  const mid = Math.floor(sortedArr.length / 2);

  return sortedArr.length % 2 !== 0 
      ? sortedArr[mid] 
      : (sortedArr[mid - 1] + sortedArr[mid]) / 2;
}

//##### DYNAMIC AUDIO TEST UI ELEMENTS ######//
let count = 12;
const count_div = document.getElementById("count_down");

// Set initial values immediately
count_div.innerHTML = `Get ready to read in: <span style="color: red;">${count}</span>`;
count_div.style.fontSize = "18px";

//######################################################//
//## SETUP TO MONITOR VOLUME LEVELS DURING AUDIO TEST //##
//######################################################//


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
      
      //When track.kind == "audio" both parties are connected, so we replace "connecting" with "connected".
      document.querySelector(".ducksoup-container .connecting").classList.add("d-none");
      document.querySelector(".ducksoup-container .noise_test").classList.remove("d-none");

      // Start countdown
      const timer = setInterval(() => {
        count--;
        count_div.innerHTML = `Get ready to read in: <span style="color: red;">${count}</span>`;
        if (count <= 0) {
          clearInterval(timer);
        }
      }, 1000);
      //Create new audio context 
      audioContext = new window.AudioContext(); //Create a new audio context where we have the streams[0] as the audio input source.
      analyser = audioContext.createAnalyser(); //Creates an analyser node to the audio context so that we can analyse properties of incoming signal.
      source = audioContext.createMediaStreamSource(streams[0]); // Create the source
      source.connect(analyser); // Connect the analyser method/node to the source. 
      dataArray = new Uint8Array(analyser.frequencyBinCount);

      // Activate logging
      volumeLoggingActive = true;
      logVolumeLevel();
      timeoutId = setTimeout(() => {
        clearInterval(timer);
        //Remove noise test UI
        document.querySelector(".ducksoup-container .noise_test").classList.add("d-none");
        //Add signal test UI
        document.querySelector(".ducksoup-container .signal_test").classList.remove("d-none");
        currentPhase = "signal"
      }, 12000);


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
    //document.querySelector(".help-container").classList.add("d-none");
    console.log("kind === 'files'");
    
  
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

    volumeLoggingActive = false;
    var medianVolume = calculateMedian(volumeLevels)
    var medianNoise = calculateMedian(noiseLevels)
    var passed = (medianVolume > 4.5) && (medianNoise < 2)
    console.log(medianVolume);
    console.log(medianNoise)

    state.ended = true;
    liveSend({
      kind: "end",
      "medianVolume": medianVolume,
      "medianNoise": medianNoise,
      "passed_test": passed
    });

    setTimeout(() => {
      document.getElementById("form").submit();
    }, 2000);

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
    console.log("ending");
    //document.querySelector(".ducksoup-container .connected").classList.add("d-none");
    //document.querySelector(".ducksoup-container .ending").classList.remove("d-none");
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