// =========================
// Variables
// =========================

const canvas = document.getElementById('wheel');
const ctx = canvas.getContext('2d');
const radius = canvas.width / 2;

const winnersList = document.getElementById('winnersList');
const clearBtn = document.getElementById('clearWinnersBtn');
const namesList = document.getElementById('namesList');

const popup = document.getElementById('winnerPopup');
const winnerNameEl = document.getElementById('winnerName');
const closePopupBtn = document.getElementById('closePopup');
const confettiContainer = document.getElementById('confettiContainer');
const spinSound = document.getElementById('spinSound');

const COLORS = [
    '#e11d48','#f97316','#f59e0b','#84cc16','#16a34a',
    '#10b981','#3b82f6','#6366f1','#8b5cf6','#7c3aed',
    '#d946ef','#fb7185'
];

const CONFETTI_COLORS = ['#f97316','#22c55e','#3b82f6','#e11d48','#a855f7','#facc15'];

let rotation = 0;      // ángulo actual en grados
let wheelData = [];
let isSpinning = false;

const SOUND_START_OFFSET = 0;

// =========================
// Utility
// =========================

function getColor(index) {
    return COLORS[index % COLORS.length];
}

// Render lista de participantes
function renderNamesList(segments) {
    if (!namesList) return;
    namesList.innerHTML = '';
    segments.forEach(seg => {
        const li = document.createElement('li');
        li.textContent = seg.name;
        li.classList.add('name-item');
        li.dataset.name = seg.name;
        namesList.appendChild(li);
    });
}

// Highlight live mientras pasa por el puntero
function highlightActiveName(name) {
    if (!namesList) return;
    const items = namesList.querySelectorAll('.name-item');
    items.forEach(li => {
        if (li.dataset.name === name) {
            li.classList.add('name-item--active');
            li.scrollIntoView({ behavior:'smooth', block:'center' });
        } else {
            li.classList.remove('name-item--active');
        }
    });
}

function clearActiveHighlight() {
    if (!namesList) return;
    const items = namesList.querySelectorAll('.name-item');
    items.forEach(li => li.classList.remove('name-item--active'));
}

// Marcar ganador en lista de participantes
function markWinnerInNamesList(name) {
    if (!namesList) return;
    const items = namesList.querySelectorAll('.name-item');
    items.forEach(li => {
        if (li.dataset.name === name) {
            li.classList.add('name-item--winner');
            li.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    });
}

// =========================
// Fetch API
// =========================

async function fetchWheelData() {
    try {
        const res = await fetch('/api/fetch');
        const data = await res.json();

        if (!res.ok || data.error) {
            alert(data.error || 'Error loading wheel data.');
            return [];
        }
        return data;
    } catch (err) {
        console.error('Fetch failed:', err);
        alert('Could not fetch data.');
        return [];
    }
}

// =========================
// Wheel Math
// =========================

function recalcAngles(segments) {
    const totalTickets = segments.reduce((sum, s) => sum + s.tickets, 0);
    if (totalTickets === 0) return [];

    let start = 0;

    return segments.map(s => {
        const angle = (s.tickets / totalTickets) * 360;
        const seg = {
            ...s,
            start_angle: start,
            end_angle: start + angle,
            angle_degrees: angle
        };
        start += angle;
        return seg;
    });
}

function drawWheel(segments) {
    let startAngle = 0;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    segments.forEach((seg, i) => {
        const angle = seg.angle_degrees * Math.PI / 180;
        const endAngle = startAngle + angle;

        ctx.beginPath();
        ctx.moveTo(radius, radius);
        ctx.arc(radius, radius, radius, startAngle, endAngle);
        ctx.fillStyle = getColor(i);
        ctx.fill();
        ctx.closePath();

        const midAngle = startAngle + angle / 2;
        ctx.save();
        ctx.translate(radius, radius);
        ctx.rotate(midAngle);
        ctx.textAlign = 'right';
        ctx.fillStyle = '#000';
        ctx.font = '14px Arial';
        ctx.fillText(seg.name, radius - 10, 5);
        ctx.restore();

        startAngle = endAngle;
    });
}

function getWinner(rotationDegrees, segments) {
    const normalized = (360 - (rotationDegrees % 360)) % 360;
    let currentAngle = 0;
    for (const seg of segments) {
        if (
            normalized >= currentAngle &&
            normalized < currentAngle + seg.angle_degrees
        ) {
            return seg.name;
        }
        currentAngle += seg.angle_degrees;
    }
    return segments[segments.length - 1].name;
}

// =========================
// Confetti
// =========================

function createConfetti() {
    if (!confettiContainer) return;

    confettiContainer.innerHTML = '';
    const pieces = 100;

    for (let i = 0; i < pieces; i++) {
        const piece = document.createElement('div');
        piece.classList.add('confetti-piece');
        piece.style.left = Math.random() * 100 + '%';
        piece.style.backgroundColor =
            CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)];
        piece.style.animationDelay = Math.random() * 0.7 + 's';
        confettiContainer.appendChild(piece);
    }

    setTimeout(() => {
        confettiContainer.innerHTML = '';
    }, 2000);
}

// =========================
// POPUP
// =========================

function showWinnerPopup(name) {
    winnerNameEl.textContent = name;
    createConfetti();
    popup.classList.remove('hidden');
}

closePopupBtn.addEventListener('click', () => {
    popup.classList.add('hidden');
    if (confettiContainer) confettiContainer.innerHTML = '';
});

// =========================
// Spin Animation
// =========================

function animateSpin(extraDegrees, duration, onEnd) {
    const startRotation = rotation;
    const targetRotation = rotation + extraDegrees;
    const startTime = performance.now();

    isSpinning = true;

    function step(now) {
        const elapsed = now - startTime;
        const t = Math.min(elapsed / duration, 1);
        const eased = 1 - Math.pow(1 - t, 3); // ease-out

        rotation = startRotation + (targetRotation - startRotation) * eased;
        canvas.style.transform = `rotate(${rotation}deg)`;

        const currentName = getWinner(rotation, wheelData);
        if (currentName) highlightActiveName(currentName);

        if (t < 1) {
            requestAnimationFrame(step);
        } else {
            isSpinning = false;
            clearActiveHighlight();
            if (onEnd) onEnd();
        }
    }

    requestAnimationFrame(step);
}

// =========================
// Event Listeners
// =========================

// Cargar ruleta al inicio
fetchWheelData().then(data => {
    if (!data.length) return;
    wheelData = recalcAngles(data);
    drawWheel(wheelData);
    renderNamesList(wheelData);
});

document.getElementById('fetchBtn').addEventListener('click', async () => {
    const data = await fetchWheelData();
    if (!data.length) return;

    wheelData = recalcAngles(data);
    drawWheel(wheelData);
    renderNamesList(wheelData);
    alert('Wheel updated!');
});

document.getElementById('spinBtn').addEventListener('click', () => {
    if (isSpinning) return;
    if (wheelData.length === 0) {
        alert('No more participants left!');
        return;
    }

    // duración total del spin (y del momento del popup) ~ 9 s
    const duration = 9500;

    // ---------- SONIDO ----------
    if (spinSound) {
        try {
            spinSound.pause();                      // por si venía de antes
            spinSound.currentTime = SOUND_START_OFFSET;
            spinSound.play();
        } catch (e) {
            console.warn('No se pudo reproducir el sonido:', e);
        }
    }

    // ---------- ANIMACIÓN ----------
    const extra = Math.random() * 360 + 720; // al menos 2 vueltas
    animateSpin(extra, duration, () => {
        // Aquí termina el spin Y sale el popup al mismo tiempo

        const winner = getWinner(rotation, wheelData);

        // Panel de winners
        const li = document.createElement('li');
        li.textContent = winner;
        li.classList.add('winner-item');
        winnersList.appendChild(li);

        // Marcar ganador en lista de participantes
        markWinnerInNamesList(winner);

        // Eliminar ganador de la ruleta
        wheelData = wheelData.filter(seg => seg.name !== winner);
        wheelData = recalcAngles(wheelData);
        drawWheel(wheelData);

        // Popup inmediato al terminar el spin
        showWinnerPopup(winner);
    });
});

clearBtn.addEventListener('click', () => {
    winnersList.innerHTML = '';
});
