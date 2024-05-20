const state = {};

const initDomRefs = async () => {
  state.audioSourceEl = document.getElementById('audio-source');
  state.videoSourceEl = document.getElementById('video-source');
  state.meterEl = document.getElementById('meter');
  state.selfieToTakeEl = document.getElementById('selfie-to-take');
  state.selfieTakenEl = document.getElementById('selfie-taken');
  state.streamEl = document.getElementById('stream');
  state.selfieEl = document.getElementById('selfie');
  state.takeSnapshotEl = document.getElementById('take-snapshot');
  state.okEl = document.getElementById('ok');
  state.cancelEl = document.getElementById('cancel');
};

const writeDevicesToForm = () => {
  const { audioSourceEl, videoSourceEl } = state;
  document.getElementById("audio_source_id").value = audioSourceEl.value;
  document.getElementById("video_source_id").value = videoSourceEl.value;
};

const displayAvailableDevices = async () => {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const { audioSourceEl, videoSourceEl } = state;
  for (let i = 0; i !== devices.length; ++i) {
    const device = devices[i];
    const option = document.createElement('option');
    option.value = device.deviceId;
    if (device.kind === 'audioinput') {
      option.text = device.label || `microphone ${audioSourceEl.length + 1}`;
      audioSourceEl.appendChild(option);
    } else if (device.kind === 'videoinput') {
      option.text = device.label || `camera ${videoSourceEl.length + 1}`;
      videoSourceEl.appendChild(option);
    }
  }
  writeDevicesToForm()
};

const udpateVolumeMeter = async () => {
  const { audioContext, audioStream, micNode, meterEl } = state;
  if (micNode) {
    micNode.disconnect();
  }
  if (audioStream && audioContext) {
    const micNode = audioContext.createMediaStreamSource(audioStream);
    state.micNode = micNode;
    const volumeMeterNode = new AudioWorkletNode(audioContext, 'volume-meter');   
    volumeMeterNode.port.onmessage = ({data}) => {
      const volume = data * 500;
      meterEl.style.width = volume + '%';
    };
    micNode.connect(volumeMeterNode).connect(audioContext.destination);
  }
};

const updateAudioStream = async () => {
  const { audioStream, audioSourceEl } = state;
  // cleanup
  if (audioStream) audioStream.getTracks().forEach(track => track.stop());
  // get new devices ids
  const audioDeviceId = audioSourceEl.value;
  writeDevicesToForm();
  // define new constraints
  const audioConstraints = {
    audio: { deviceId: audioDeviceId ? { exact: audioDeviceId } : undefined },
    video: false
  };
  // get new stream
  return navigator.mediaDevices.getUserMedia(audioConstraints).then((newStream) => {
    // save to be able to stop later
    state.audioStream = newStream;
    udpateVolumeMeter();
  });
};

const updateVideoStream = () => {
  const { videoStream, streamEl, videoSourceEl } = state;
  // cleanup
  if (videoStream) videoStream.getTracks().forEach(track => track.stop());
  // get new devices ids
  const videoDeviceId = videoSourceEl.value;
  writeDevicesToForm();
  // define new constraints
  const videoConstraints = {
    audio: false,
    video: {
        deviceId: videoDeviceId ? { exact: videoDeviceId } : undefined,
        width: { ideal: 640 },
        height: { ideal: 480 }
    }
  };
  return navigator.mediaDevices.getUserMedia(videoConstraints).then((newStream) => {
    document.getElementById("ok").classList.remove("d-none");
    // save to be able to stop later
    state.videoStream = newStream;
    // display video
    streamEl.srcObject = newStream;
  });
};

const updateStreams = async () => {
  await updateAudioStream();
  await updateVideoStream();
}

const init = async () => {
  initDomRefs();
  try {
    await updateStreams();
  } catch (error) {
    alert("Unable to access your webcam. Please close other browsers or applications using it, then refresh this page.")
  }
  await displayAvailableDevices();

  const { takeSnapshotEl, okEl, cancelEl, streamEl, selfieEl, selfieToTakeEl, selfieTakenEl, audioSourceEl, videoSourceEl } = state;
  takeSnapshotEl.addEventListener("click", (e) => {
    e.preventDefault();
    selfieEl.width = streamEl.videoWidth;
    selfieEl.height = streamEl.videoHeight;
    selfieEl.getContext('2d').drawImage(streamEl, 0, 0, selfieEl.width, selfieEl.height);
    selfieToTakeEl.classList.add("d-none")
    selfieTakenEl.classList.remove("d-none")
  });

  cancelEl.addEventListener("click", (e) => {
    e.preventDefault();
    selfieToTakeEl.classList.remove("d-none")
    selfieTakenEl.classList.add("d-none")
  });

  okEl.addEventListener("click", (e) => {
    document.getElementById("image_data").value = selfieEl.toDataURL('image/jpeg', 1.0);
  });

  audioSourceEl.addEventListener("change", updateAudioStream);
  videoSourceEl.addEventListener("change", updateVideoStream);
  liveSend({'kind': 'start'});
};

window.liveRecv = async (data) => {
  if (data === "start") {
    state.audioContext = new AudioContext();
    await state.audioContext.audioWorklet.addModule('/static/global/lib/volume-meter.js');
    udpateVolumeMeter();
  }
}

document.addEventListener('DOMContentLoaded', init);
