let audio = (audioSrc = ctx = gain = null),
  gain_val = 0.5;
let loop_bool = false;

let start = () => {
  console.log("started");

  ctx = new AudioContext();
  gain = ctx.createGain();
  gain.gain.setValueAtTime(0.5, ctx.currentTime);
  gain.connect(ctx.destination);

  let btns = document.getElementsByTagName("button");
  for (let e of btns) {
    e.addEventListener("click", fire_sound);
  }

  document.querySelector("#gain").addEventListener("input", set);
  document.querySelector("#loop").addEventListener("input", loop);
};

let loop = (e) => {
  console.log("setting loop: " + e.target.checked);
  if (e.target.checked) {
    if (audio !== null) {
      audio.loop = !0;
    }
    loop_bool = !0;
  } else {
    if (audio !== null) {
      audio.loop = !1;
    }
    loop_bool = !1;
  }
};

let set = (e) => {
  if (e.target.validity.rangeOverflow) {
    e.target.value = 100;
  } else if (e.target.validity.rangeUnderflow) {
    e.target.value = 0;
  }
  gain_val = e.target.value / 100;
  console.log("set gain: " + gain_val);
  if (audio !== null) {
    gain.gain.linearRampToValueAtTime(gain_val, ctx.currentTime + 0.3);
  }
};

// Generalized sound player.
let fire_sound = (e) => {
  if (ctx.state == "suspended") {
    ctx.resume();
  }

  if (audio != null) {
    audio.pause();
  }
  // The h5 in the button can't have a name attribute.
  if (!e.target.name) {
    //Go up a step and get the name.
    tempAudio = new Audio("./audio/" + e.target.parentElement.name);
  } else {
    // Get the name from the button.
    tempAudio = new Audio("./audio/" + e.target.name);
  }
  if (audio == null || audio.ended || audio.src !== tempAudio.src) {
    audio = tempAudio;
    audio.loop = loop_bool;
    audioSrc = ctx.createMediaElementSource(audio);
    audioSrc.connect(gain);
    audio.play();
  } else {
    audio = null;
  }
};

document.addEventListener("DOMContentLoaded", start, { once: !0 });
