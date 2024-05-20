document.addEventListener("DOMContentLoaded", async () => {
  const canvas = document.getElementById("selfie");
  const ctx = canvas.getContext("2d");

  const image = new Image();
  image.onload = function () {
    canvas.width = image.width;
    canvas.height = image.height;
    ctx.drawImage(image, 0, 0, image.width, image.height);
  };
  image.src = js_vars.other_player_image_data;

  // inspect client state
  if (typeof navigator.getBattery === "function") {
    const battery = await navigator.getBattery();
    document.getElementById("inspect_battery_charging").value = battery.charging;
    document.getElementById("inspect_battery_level").value = battery.level;
  }
  if (typeof navigator.connection !== "undefined") {
    document.getElementById("inspect_connection_effective_type").value = navigator.connection.effectiveType;
  }
  document.getElementById("inspect_user_agent").value = navigator.userAgent;
  document.getElementById("inspect_concurrency").value = navigator.hardwareConcurrency;
  document.getElementById("inspect_device_memory").value = navigator.deviceMemory;
})