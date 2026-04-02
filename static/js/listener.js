const API_BASE = "/api/listener";

let currentListener = "wifi1";
let isRunning = false;


// ─────────────────────────────
// ▶ START LISTENER
// ─────────────────────────────
export async function startListener() {
    if (isRunning) {
        console.log("Already running");
        return;
    }

    try {
        const res = await fetch(`${API_BASE}/create`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                name: currentListener,
                interface: "wlan0",
                port: 5051
            })
        });

        const data = await res.json();
        console.log("START:", data);

        if (data.error) {
            alert(data.error);
            return;
        }

        isRunning = true;

        console.log("✅ Listener started (Realtime mode)");

    } catch (err) {
        console.error("Start error:", err);
    }
}


// ─────────────────────────────
// ⏹ STOP LISTENER
// ─────────────────────────────
export async function stopListener() {
    if (!isRunning) return;

    try {
        const res = await fetch(`${API_BASE}/stop/${currentListener}`, {
            method: "POST"
        });

        const data = await res.json();
        console.log("STOP:", data);

        isRunning = false;

        clearDevicesUI();

    } catch (err) {
        console.error("Stop error:", err);
    }
}


// ─────────────────────────────
// 🌐 MAKE GLOBAL (FIX onclick)
// ─────────────────────────────
window.startListener = startListener;
window.stopListener = stopListener;


// ─────────────────────────────
// 📡 REALTIME SOCKET LISTENER
// ─────────────────────────────
document.addEventListener("network:update", (event) => {
    if (!isRunning) return;

    const data = event.detail;
    renderDevices(data.devices || []);
});


// ─────────────────────────────
// 🧹 CLEAR UI
// ─────────────────────────────
function clearDevicesUI() {
    const container = document.getElementById("devices");
    if (!container) return;

    container.innerHTML = "<p>Listener stopped</p>";
}


// ─────────────────────────────
// 🖥 RENDER DEVICES
// ─────────────────────────────
function renderDevices(devices) {
    const container = document.getElementById("devices");
    if (!container) return;

    container.innerHTML = "";

    if (!devices || devices.length === 0) {
        container.innerHTML = "<p>No devices detected...</p>";
        return;
    }

    devices.forEach(d => {
        const div = document.createElement("div");
        div.className = "device";

        div.innerHTML = `
            <b>IP:</b> ${d.ip || "N/A"}<br>
            <b>MAC:</b> ${d.mac || "N/A"}<br>
            <b>Packets:</b> ${d.packets || 0}<br>
            <small>Last seen: ${formatTime(d.last_seen)}</small>
            <hr/>
        `;

        container.appendChild(div);
    });
}


// ─────────────────────────────
// ⏱ FORMAT TIME
// ─────────────────────────────
function formatTime(ts) {
    if (!ts) return "N/A";

    const date = new Date(ts * 1000);
    return date.toLocaleTimeString();
}
