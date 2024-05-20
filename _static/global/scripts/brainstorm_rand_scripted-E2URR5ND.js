(() => {
  // _front/src/brainstorm_rand_scripted.js
  var state = {
    fxIndex: 0,
    playing: false
  };
  var ATTACK = 700;
  var SUSTAIN = 1400;
  var RELEASE = 750;
  var FX_DURATION = ATTACK + SUSTAIN + RELEASE;
  var ALPHA_SMILE = 0.9;
  var ALPHA_NEUTRAL = 0;
  var ALPHA_UNSMILE = -0.6;
  var shuffle = (input) => {
    const output = [...input];
    for (let i = output.length - 1; i > 0; i--) {
      let j = Math.floor(Math.random() * (i + 1));
      [output[i], output[j]] = [output[j], output[i]];
    }
    return output;
  };
  var smileUnsmileArray = () => {
    const smileCount = Math.round(state.fxTotal / 2);
    const unsmileCount = state.fxTotal - smileCount;
    const unshuffled = [...Array(smileCount).fill(true), ...Array(unsmileCount).fill(false)];
    return shuffle(unshuffled);
  };
  var waitFor = () => {
    const range = state.inBetweenMean / 3;
    const randInRange = (Math.random() - 0.5) * 2 * range;
    let randTime = state.inBetweenMean + randInRange;
    if (state.fxIndex == 0) {
      randTime += 2e3;
    } else {
      randTime += FX_DURATION;
    }
    return randTime;
  };
  var controlFx = (isSmiling) => {
    const alphaFx = isSmiling ? ALPHA_SMILE : ALPHA_UNSMILE;
    console.log("[brainstorm_rs] start fx (".concat(state.fxIndex + 1, ") : ").concat(isSmiling ? "smile" : "unsmile"));
    window.ducksoup.controlFx(state.videoFxName, "alpha", alphaFx, ATTACK, state.userId);
    window.ducksoup.controlFx(state.videoFxName, "alpha", alphaFx, ATTACK, state.otherId);
    setTimeout(() => {
      window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.userId);
      window.ducksoup.controlFx(state.videoFxName, "alpha", ALPHA_NEUTRAL, RELEASE, state.otherId);
    }, SUSTAIN);
  };
  var planFx = () => {
    const isSmiling = state.fxArray[state.fxIndex];
    controlFx(isSmiling);
    state.fxIndex++;
    if (state.fxIndex == state.fxTotal)
      return;
    state.timeoutId = setTimeout(planFx, waitFor());
  };
  var init = () => {
    const { interactionDuration, fxTotal, xpOptions } = js_vars;
    if (!xpOptions.primary)
      return;
    const { videoFxName, userId, otherId } = xpOptions;
    state.videoFxName = videoFxName;
    state.userId = userId;
    state.otherId = otherId;
    state.fxTotal = fxTotal;
    state.fxArray = smileUnsmileArray();
    state.interactionDuration = interactionDuration * 1e3;
    state.inBetweenMean = (state.interactionDuration - state.fxTotal * FX_DURATION) / (state.fxTotal + 1);
    console.log("[Brainstorm] interactionDuration: ".concat(state.interactionDuration, "  inBetweenMean: ").concat(state.inBetweenMean));
    window.addPlayerListener((data) => {
      const { kind } = data;
      if (kind == "play" && !state.playing) {
        console.log("[brainstorm_rs] playing");
        state.playing = true;
        state.timeoutId = setTimeout(planFx, waitFor());
      } else if (kind == "end") {
        clearTimeout(state.timeoutId);
      }
    });
  };
  document.addEventListener("DOMContentLoaded", init);
})();
