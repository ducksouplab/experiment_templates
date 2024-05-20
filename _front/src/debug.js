console.log("[Debug] v0.10.1");

const state = {
  visibility: ""
};

const init = () => {
  document.getElementById("info").innerHTML = JSON.stringify({ js_vars }, null, 2);
    const mountEl = document.getElementById("ducksoup-root");
};

// callback from python
window.liveRecv = (data) => {
  if(data === 'next') {   
    setTimeout(() => {
      document.getElementById("form").submit();
    }, 2000);
  }    
}

document.addEventListener("DOMContentLoaded", init);

document.addEventListener('visibilitychange', () => {
  state.visibility += `${(new Date()).toLocaleTimeString()}-> ${document.visibilityState} | `;
});