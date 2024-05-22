const state = {
  fxIndex: 0,
  playing: false
};

// 
const ATTACK = 700; 
const SUSTAIN = 1400; 
const RELEASE = 750; 
const FX_DURATION = ATTACK + SUSTAIN + RELEASE; 
const ALPHA_SMILE = 0.8; 
const ALPHA_NEUTRAL = 0; 
const ALPHA_UNSMILE = -0.4;

// from https://javascript.info/task/shuffle
const shuffle = (input) => {
  const output = [...input];
  for (let i = output.length - 1; i > 0; i--) {
    let j = Math.floor(Math.random() * (i + 1));
    [output[i], output[j]] = [output[j], output[i]];
  }
  return output;
}

const smileUnsmileArray = () => {
  const smileCount = Math.round(state.fxTotal/2);
  const unsmileCount = state.fxTotal - smileCount;
  const unshuffled = [...Array(smileCount).fill(true), ...Array(unsmileCount).fill(false)];
  return shuffle(unshuffled);
}

const waitFor = () => {
  const range = state.inBetweenMean / 3;
  // from 0:1 to -range:range
  const randInRange = (Math.random() - 0.5) * 2 * range;
  let randTime = state.inBetweenMean + randInRange;
  if (state.fxIndex == 0) {
    randTime += 2000; // 2 seconds: empirical initial connecting delay
  } else {
    randTime += FX_DURATION
  }
  return randTime;
}

const controlFx = (isSmiling) => {
  const alphaFx = isSmiling ? ALPHA_SMILE : ALPHA_UNSMILE;
  console.log(`[brainstorm_rs] start fx (${state.fxIndex + 1}) : ${isSmiling ? "smile" : "unsmile"}`);
  window.ducksoup.controlFx(state.videoFxName, "alpha", alphaFx, ATTACK, state.userId);
  window.ducksoup.controlFx(state.videoFxName, "alpha", alphaFx, ATTACK, state.otherId);
  setTimeout(() => {
    window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.userId);
    window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.otherId);
  }, SUSTAIN);
}

const planFx = () => {
  // smile or unsmile
  const isSmiling = state.fxArray[state.fxIndex];
  controlFx(isSmiling);
  
  // plan next fx
  state.fxIndex++;
  if (state.fxIndex == state.fxTotal) return; // no more fx
  state.timeoutId = setTimeout(planFx, waitFor());
};

const init = () => {
  const { interactionDuration, fxTotal, xpOptions } = js_vars;
  // primary controls fx of both participants
  if (!xpOptions.primary) return;

  const { videoFxName, userId, otherId} = xpOptions;
  state.videoFxName = videoFxName;
  state.userId = userId;
  state.otherId = otherId;
  state.fxTotal = fxTotal;  
  state.fxArray = smileUnsmileArray();
  state.interactionDuration = interactionDuration * 1000;
  // total(off) = duration - duration(smiles)
  // count(off) = count(smile) + 1 (because start->off->smile->off->smile->off->end)
  // IN_BETWEEN_MEAN = total(off) / count(off)
  state.inBetweenMean = (state.interactionDuration - state.fxTotal * FX_DURATION) / (state.fxTotal + 1);
  console.log(`[Brainstorm] interactionDuration: ${state.interactionDuration}  inBetweenMean: ${state.inBetweenMean}`);

  // callback from DuckSoup
  window.addPlayerListener((data) => {
    const { kind } = data;
    if(kind == "play" && !state.playing) {
      console.log("[brainstorm_rs] playing");
      state.playing = true;
      // plan first fx
      state.timeoutId = setTimeout(planFx, waitFor())
    } else if(kind == "end") {
      clearTimeout(state.timeoutId);
    } 
  });
}

// 
document.addEventListener("DOMContentLoaded", init);