const ATTACK = 300;

const init = async () => {
  const alpha = js_vars.xpOptions.alpha;
  
  window.addWidthThresholdListener((ok) => {
    console.log("[DuckSoup now!] width threshold: " + ok);
    if(ok) {
      window.ducksoup.controlFx("video_fx", "alpha", alpha, 300);
    } else {
      window.ducksoup.controlFx("video_fx", "alpha", 0, 300);
    }
  });
};

document.addEventListener("DOMContentLoaded", init);