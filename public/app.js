// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/sw.js').catch(err => {
        console.error('Service Worker registration failed:', err);
    });
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

// PWA Install Prompt Logic
let deferredPrompt = null;
const installBanner = document.getElementById('pwa-install-banner');
const installBtn = document.getElementById('pwa-install-btn');
const closeBtn = document.getElementById('pwa-close-btn');
const pwaDesc = document.getElementById('pwa-desc');

// Detect iOS
const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream;
// Detect standalone mode (already installed)
const isStandalone = window.matchMedia('(display-mode: standalone)').matches;

function initPwaPrompt() {
    const isDismissed = localStorage.getItem('pwa-prompt-dismissed');
    if (isDismissed || isStandalone) return;

    if (isIOS) {
        // Customize text for iOS
        if (pwaDesc) {
            pwaDesc.textContent = 'Tap Share > Add to Home Screen';
        }
        if (installBtn) {
            installBtn.style.display = 'none'; // Hide install button since iOS needs manual share sheet
        }
        if (installBanner) {
            installBanner.classList.remove('hidden');
        }
    } else {
        window.addEventListener('beforeinstallprompt', (e) => {
            // Prevent the mini-infobar from appearing on mobile
            e.preventDefault();
            // Stash the event so it can be triggered later.
            deferredPrompt = e;
            // Update UI to notify the user they can install the PWA
            if (installBanner) {
                installBanner.classList.remove('hidden');
            }
        });
    }

    if (installBtn) {
        installBtn.addEventListener('click', async () => {
            if (!deferredPrompt) return;
            // Show the install prompt
            deferredPrompt.prompt();
            // Wait for the user to respond to the prompt
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            // We've used the prompt, and can't use it again, clear it
            deferredPrompt = null;
            hideInstallBanner();
        });
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', () => {
            localStorage.setItem('pwa-prompt-dismissed', 'true');
            hideInstallBanner();
        });
    }
}

function hideInstallBanner() {
    if (installBanner) {
        installBanner.classList.add('hidden');
    }
}

// Initialize PWA prompt setup
initPwaPrompt();
