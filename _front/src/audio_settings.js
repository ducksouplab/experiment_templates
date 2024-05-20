const state = {};

const initDomRefs = async () => {
  state.audioSourceEl = document.getElementById('audio-source');
  state.meterEl = document.getElementById('meter');
};

const writeDevicesToForm = () => {
  const { audioSourceEl } = state;
  document.getElementById("audio_source_id").value = audioSourceEl.value;
};

const displayAvailableDevices = async () => {
  const devices = await navigator.mediaDevices.enumerateDevices();
  const { audioSourceEl } = state;
  for (let i = 0; i !== devices.length; ++i) {
    const device = devices[i];
    const option = document.createElement('option');
    option.value = device.deviceId;
    if (device.kind === 'audioinput') {
      option.text = device.label || `microphone ${audioSourceEl.length + 1}`;
      audioSourceEl.appendChild(option);
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
      let volume = data * 750;
      if (volume > 100) {
        volume = 100;
      }
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

const updateStreams = async () => {
  await updateAudioStream();
}

const init = async () => {
  initDomRefs();
  try {
    await updateStreams();
  } catch (error) {
    alert("Unable to access your webcam. Please close other browsers or applications using it, then refresh this page.")
  }
  await displayAvailableDevices();

  const { audioSourceEl } = state;
  audioSourceEl.addEventListener("change", updateAudioStream);
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
