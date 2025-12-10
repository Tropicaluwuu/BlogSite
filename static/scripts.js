console.log("JS Loaded");


function randomRainbowColor() {
    const hue = Math.floor(Math.random() * 360);
    return `hsl(${hue}, 90%, 65%)`;
}

function createSparkle(x, y) {
    const s = document.createElement("div");
    s.className = "sparkle";

    
    s.style.left = x + "px";
    s.style.top = y + "px";

    
    s.style.background = randomRainbowColor();

  
    const size = 12 + Math.random() * 18;
    s.style.width = size + "px";
    s.style.height = size + "px";

    document.body.appendChild(s);

    setTimeout(() => s.remove(), 900);
}


document.addEventListener("pointermove", (event) => {
    const x = event.pageX; 
    const y = event.pageY;
    createSparkle(x, y);
});
