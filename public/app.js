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

// Add event listeners to all buttons
document.querySelectorAll('button[data-action]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        // Prevent double firing on touch devices
        e.preventDefault();
        sendCommand(btn.getAttribute('data-action'));
    });
    // Add touchstart for better responsiveness on mobile
    btn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        sendCommand(btn.getAttribute('data-action'));
    });
});

document.querySelectorAll('button[data-app]').forEach(btn => {
    btn.addEventListener('click', (e) => {
        e.preventDefault();
        launchApp(btn.getAttribute('data-app'));
    });
    btn.addEventListener('touchstart', (e) => {
        e.preventDefault();
        launchApp(btn.getAttribute('data-app'));
    });
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
