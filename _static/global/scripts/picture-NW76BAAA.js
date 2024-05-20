(() => {
  // _front/src/picture.js
  var state = {};
  var initDomRefs = async () => {
    state.audioSourceEl = document.getElementById("audio-source");
    state.videoSourceEl = document.getElementById("video-source");
    state.meterEl = document.getElementById("meter");
    state.selfieToTakeEl = document.getElementById("selfie-to-take");
    state.selfieTakenEl = document.getElementById("selfie-taken");
    state.streamEl = document.getElementById("stream");
    state.selfieEl = document.getElementById("selfie");
    state.takeSnapshotEl = document.getElementById("take-snapshot");
    state.okEl = document.getElementById("ok");
    state.cancelEl = document.getElementById("cancel");
  };
  var writeDevicesToForm = () => {
    const { audioSourceEl, videoSourceEl } = state;
    document.getElementById("audio_source_id").value = audioSourceEl.value;
    document.getElementById("video_source_id").value = videoSourceEl.value;
  };
  var displayAvailableDevices = async () => {
    const devices = await navigator.mediaDevices.enumerateDevices();
    const { audioSourceEl, videoSourceEl } = state;
    for (let i = 0; i !== devices.length; ++i) {
      const device = devices[i];
      const option = document.createElement("option");
      option.value = device.deviceId;
      if (device.kind === "audioinput") {
        option.text = device.label || "microphone ".concat(audioSourceEl.length + 1);
        audioSourceEl.appendChild(option);
      } else if (device.kind === "videoinput") {
        option.text = device.label || "camera ".concat(videoSourceEl.length + 1);
        videoSourceEl.appendChild(option);
      }
    }
    writeDevicesToForm();
  };
  var udpateVolumeMeter = async () => {
    const { audioContext, audioStream, micNode, meterEl } = state;
    if (micNode) {
      micNode.disconnect();
    }
    if (audioStream && audioContext) {
      const micNode2 = audioContext.createMediaStreamSource(audioStream);
      state.micNode = micNode2;
      const volumeMeterNode = new AudioWorkletNode(audioContext, "volume-meter");
      volumeMeterNode.port.onmessage = ({ data }) => {
        const volume = data * 500;
        meterEl.style.width = volume + "%";
      };
      micNode2.connect(volumeMeterNode).connect(audioContext.destination);
    }
  };
  var updateAudioStream = async () => {
    const { audioStream, audioSourceEl } = state;
    if (audioStream)
      audioStream.getTracks().forEach((track) => track.stop());
    const audioDeviceId = audioSourceEl.value;
    writeDevicesToForm();
    const audioConstraints = {
      audio: { deviceId: audioDeviceId ? { exact: audioDeviceId } : void 0 },
      video: false
    };
    return navigator.mediaDevices.getUserMedia(audioConstraints).then((newStream) => {
      state.audioStream = newStream;
      udpateVolumeMeter();
    });
  };
  var updateVideoStream = () => {
    const { videoStream, streamEl, videoSourceEl } = state;
    if (videoStream)
      videoStream.getTracks().forEach((track) => track.stop());
    const videoDeviceId = videoSourceEl.value;
    writeDevicesToForm();
    const videoConstraints = {
      audio: false,
      video: {
        deviceId: videoDeviceId ? { exact: videoDeviceId } : void 0,
        width: { ideal: 640 },
        height: { ideal: 480 }
      }
    };
    return navigator.mediaDevices.getUserMedia(videoConstraints).then((newStream) => {
      document.getElementById("ok").classList.remove("d-none");
      state.videoStream = newStream;
      streamEl.srcObject = newStream;
    });
  };
  var updateStreams = async () => {
    await updateAudioStream();
    await updateVideoStream();
  };
  var init = async () => {
    initDomRefs();
    try {
      await updateStreams();
    } catch (error) {
      alert("Unable to access your webcam. Please close other browsers or applications using it, then refresh this page.");
    }
    await displayAvailableDevices();
    const { takeSnapshotEl, okEl, cancelEl, streamEl, selfieEl, selfieToTakeEl, selfieTakenEl, audioSourceEl, videoSourceEl } = state;
    takeSnapshotEl.addEventListener("click", (e) => {
      e.preventDefault();
      selfieEl.width = streamEl.videoWidth;
      selfieEl.height = streamEl.videoHeight;
      selfieEl.getContext("2d").drawImage(streamEl, 0, 0, selfieEl.width, selfieEl.height);
      selfieToTakeEl.classList.add("d-none");
      selfieTakenEl.classList.remove("d-none");
    });
    cancelEl.addEventListener("click", (e) => {
      e.preventDefault();
      selfieToTakeEl.classList.remove("d-none");
      selfieTakenEl.classList.add("d-none");
    });
    okEl.addEventListener("click", (e) => {
      document.getElementById("image_data").value = selfieEl.toDataURL("image/jpeg", 1);
    });
    audioSourceEl.addEventListener("change", updateAudioStream);
    videoSourceEl.addEventListener("change", updateVideoStream);
    liveSend({ "kind": "start" });
  };
  window.liveRecv = async (data) => {
    if (data === "start") {
      state.audioContext = new AudioContext();
      await state.audioContext.audioWorklet.addModule("/static/global/lib/volume-meter.js");
      udpateVolumeMeter();
    }
  };
  document.addEventListener("DOMContentLoaded", init);
})();
