const text = document.querySelector('.floating-text');
const waveContainer = document.querySelector('.wave-container');

/* TEXT LOOP */
const messages = [
  "Hello there!",
  "I'm your AI",
  "Ask me anything",
  "Ready when you are"
];

function showText(msg) {
  text.style.opacity = 0;
  setTimeout(() => {
    text.textContent = msg;
    text.style.opacity = 1;
  }, 300);

  setTimeout(() => {
    text.style.opacity = 0;
  }, 2500);
}

setInterval(() => {
  const msg = messages[Math.floor(Math.random() * messages.length)];
  showText(msg);
}, 3000);

/* WAVES */
for (let i = 0; i < 40; i++) {
  const wave = document.createElement('div');
  wave.className = 'wave';
  wave.style.animationDelay = `${Math.random()}s`;
  waveContainer.appendChild(wave);
}