const slides = [
  { image: "../zfhstech.com-mirror/images/bg-1.png", title: "slide 1" },
  { image: "../zfhstech.com-mirror/images/bg-2.png", title: "slide 2" },
  { image: "../zfhstech.com-mirror/images/bg-3.png", title: "slide 3" },
  { image: "../zfhstech.com-mirror/images/bg-4.png", title: "slide 4" },
];

const stage = document.querySelector("#carouselStage");
const pagination = document.querySelector("#carouselPagination");
const prevButton = document.querySelector(".carousel-button.prev");
const nextButton = document.querySelector(".carousel-button.next");

let activeIndex = 0;
let autoplayTimer = null;
let touchStartX = 0;

function wrapIndex(index) {
  return (index + slides.length) % slides.length;
}

function shortestOffset(index, active) {
  let offset = index - active;
  const half = slides.length / 2;
  if (offset > half) offset -= slides.length;
  if (offset < -half) offset += slides.length;
  return offset;
}

function render() {
  stage.innerHTML = "";
  pagination.innerHTML = "";

  slides.forEach((slide, index) => {
    const offset = shortestOffset(index, activeIndex);
    const abs = Math.abs(offset);
    const el = document.createElement("button");
    el.type = "button";
    el.className = `carousel-slide${index === activeIndex ? " is-active" : ""}`;
    el.style.backgroundImage = `url("${slide.image}")`;
    el.style.zIndex = String(10 - abs);
    el.style.opacity = abs > 2 ? "0" : "1";
    el.style.pointerEvents = abs > 2 ? "none" : "auto";
    el.setAttribute("aria-label", slide.title);

    const x = offset * 520;
    const rotateY = offset * -50;
    const depth = abs * -100;
    const scale = index === activeIndex ? 1.05 : Math.max(0.78, 1 - abs * 0.13);
    el.style.transform = `translate3d(calc(-50% + ${x}px), 0, ${depth}px) rotateY(${rotateY}deg) scale(${scale})`;

    el.addEventListener("click", () => {
      if (index !== activeIndex) goTo(index);
    });
    stage.appendChild(el);

    const dot = document.createElement("button");
    dot.type = "button";
    dot.className = `carousel-dot${index === activeIndex ? " is-active" : ""}`;
    dot.setAttribute("aria-label", `切换到第 ${index + 1} 张`);
    dot.addEventListener("click", () => goTo(index));
    pagination.appendChild(dot);
  });
}

function goTo(index) {
  activeIndex = wrapIndex(index);
  render();
  restartAutoplay();
}

function next() {
  goTo(activeIndex + 1);
}

function prev() {
  goTo(activeIndex - 1);
}

function startAutoplay() {
  stopAutoplay();
  autoplayTimer = window.setInterval(next, 4000);
}

function stopAutoplay() {
  if (autoplayTimer) {
    window.clearInterval(autoplayTimer);
    autoplayTimer = null;
  }
}

function restartAutoplay() {
  startAutoplay();
}

prevButton.addEventListener("click", prev);
nextButton.addEventListener("click", next);

stage.addEventListener("mouseenter", stopAutoplay);
stage.addEventListener("mouseleave", startAutoplay);

stage.addEventListener("touchstart", event => {
  touchStartX = event.touches[0].clientX;
  stopAutoplay();
});

stage.addEventListener("touchend", event => {
  const delta = event.changedTouches[0].clientX - touchStartX;
  if (Math.abs(delta) > 45) {
    delta < 0 ? next() : prev();
  } else {
    startAutoplay();
  }
});

render();
startAutoplay();
