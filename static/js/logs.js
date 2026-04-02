// static/js/logs.js

let logBox = null;

// ─────────────────────────────
// ✅ INIT FUNCTION (REQUIRED)
// ─────────────────────────────
export function initLogs() {
    console.log("📡 Logs module initialized");

    logBox = document.getElementById("systemLogs");

    if (!logBox) {
        console.warn("⚠️ systemLogs div not found");
        return;
    }

    // Wait a bit to ensure socket is ready
    setTimeout(() => {
        attachSocketListeners();
    }, 200);
}

// ─────────────────────────────
// 🔌 ATTACH SOCKET EVENTS SAFELY
// ─────────────────────────────
function attachSocketListeners() {
    if (!socket) {
        console.error("❌ Socket not initialized yet");
        return;
    }

    // CONNECT
    socket.on("connect", () => {
        console.log("✅ Connected to server (logs)");
    });

    // RECEIVE LOGS
    socket.on("log", (data) => {
        console.log("📥 Log received:", data);
        addLog(data);
    });
}

// ─────────────────────────────
// 📥 ADD LOG TO UI
// ─────────────────────────────
function addLog(data) {
    if (!logBox) return;

    const line = document.createElement("div");
    line.className = "log-line";

    line.textContent = `[${data.time}] ${data.message}`;

    logBox.appendChild(line);

    // AUTO SCROLL
    logBox.scrollTop = logBox.scrollHeight;
}
