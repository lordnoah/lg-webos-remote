// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js')
    .then(reg => {
        console.log('Service Worker registered successfully with scope:', reg.scope);
    })
    .catch(err => {
        console.error('Service Worker registration failed. Note: PWAs require HTTPS or localhost to run service workers:', err);
    });
} else {
    console.warn('Service workers are not supported by this browser.');
}

// Function to trigger haptic feedback if supported
function vibrate() {
    if (navigator.vibrate) {
        navigator.vibrate(50); // 50ms short vibration
    }
}

// Function to send command to backend
async function sendCommand(action) {
    vibrate();
    try {
        const response = await fetch('/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action })
        });
        if (!response.ok) {
            console.error('Failed to send command:', await response.text());
        }
    } catch (e) {
        console.error('Network error:', e);
    }
}

// Function to launch app
async function launchApp(appId) {
    vibrate();
    try {
        const response = await fetch('/api/launch', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ app_id: appId })
        });
        if (!response.ok) {
            console.error('Failed to launch app:', await response.text());
        }
    } catch (e) {
        console.error('Network error:', e);
    }
}

// Track timestamp to prevent synthetic clicks from firing after touchend
let lastTouchTime = 0;

function attachTapHandler(element, callback) {
    let startX = 0;
    let startY = 0;
    let isSwiping = false;

    element.addEventListener('touchstart', (e) => {
        if (e.touches.length === 1) {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            isSwiping = false;
            element.classList.add('btn-active');
        }
    }, { passive: true });

    element.addEventListener('touchmove', (e) => {
        if (e.touches.length === 1) {
            const dx = e.touches[0].clientX - startX;
            const dy = e.touches[0].clientY - startY;
            // Movement > 8px indicates a swipe/scroll gesture, cancel tap
            if (Math.hypot(dx, dy) > 8) {
                isSwiping = true;
                element.classList.remove('btn-active');
            }
        }
    }, { passive: true });

    element.addEventListener('touchend', (e) => {
        setTimeout(() => element.classList.remove('btn-active'), 120);
        if (!isSwiping) {
            lastTouchTime = Date.now();
            e.preventDefault();
            callback();
        }
    });

    element.addEventListener('touchcancel', () => {
        isSwiping = true;
        element.classList.remove('btn-active');
    });

    element.addEventListener('click', (e) => {
        // Prevent double firing if touchend already handled this interaction
        if (Date.now() - lastTouchTime < 500) {
            return;
        }
        element.classList.add('btn-active');
        setTimeout(() => element.classList.remove('btn-active'), 120);
        callback();
    });
}

// Add event listeners to all buttons using gesture-safe tap handler
document.querySelectorAll('button[data-action]').forEach(btn => {
    attachTapHandler(btn, () => sendCommand(btn.getAttribute('data-action')));
});

document.querySelectorAll('button[data-app]').forEach(btn => {
    attachTapHandler(btn, () => launchApp(btn.getAttribute('data-app')));
});

// Prevent long-press context menu on mobile
window.oncontextmenu = function(event) {
    event.preventDefault();
    event.stopPropagation();
    return false;
};

// Fullscreen API Logic
const fullscreenBtn = document.getElementById('fullscreen-btn');
if (fullscreenBtn) {
    // Detect iOS
    const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
    // Detect standalone mode (already installed)
    const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone;

    // Only show fullscreen button if NOT on iOS AND NOT in standalone mode
    if (!isIOS && !isStandalone) {
        fullscreenBtn.style.display = 'flex';
    }

    const toggleFullscreen = () => {
        if (!document.fullscreenElement) {
            document.documentElement.requestFullscreen().catch(err => {
                console.error(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            }
        }
    };
    fullscreenBtn.addEventListener('click', toggleFullscreen);
    fullscreenBtn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        toggleFullscreen();
    });
}
