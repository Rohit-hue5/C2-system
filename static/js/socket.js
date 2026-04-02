// static/js/socket.js

let socketInstance = null;

// GLOBAL STATE
window.app = window.app || {
    agents: {},
    stats: {},
    connected: false,
    lastUpdate: null
};

// ─────────────────────────────
// ✅ GET SOCKET
// ─────────────────────────────
export function getSocket() {
    return socketInstance;
}

// ─────────────────────────────
// 🚀 INIT SOCKET (FULLY FIXED)
// ─────────────────────────────
export function initSocket() {
    if (socketInstance) {
        console.log("⚠ Socket already initialized");
        return socketInstance;
    }

    console.log("🚀 Initializing Socket...");

    socketInstance = window.io({
        transports: ["websocket", "polling"],
        reconnection: true,
        reconnectionAttempts: 10,
        reconnectionDelay: 1000,
        timeout: 5000
    });

    window.socket = socketInstance;

    // ─────────────────────────────
    // 🔌 CONNECTION EVENTS
    // ─────────────────────────────
    socketInstance.on("connect", () => {
        console.log("✅ Socket connected:", socketInstance.id);

        window.app.connected = true;

        dispatch("socket:connected");
    });

    socketInstance.on("disconnect", () => {
        console.log("❌ Socket disconnected");

        window.app.connected = false;

        dispatch("socket:disconnected");
    });

    socketInstance.on("connect_error", (err) => {
        console.error("❌ Socket connection error:", err);
    });

    socketInstance.io.on("reconnect_attempt", () => {
        console.log("🔄 Reconnecting...");
    });

    socketInstance.io.on("reconnect", () => {
        console.log("✅ Reconnected");
    });

    // ─────────────────────────────
    // 📦 INITIAL STATE
    // ─────────────────────────────
    socketInstance.on("init", data => {
        console.log("📦 INIT RECEIVED:", data);

        if (!data) return;

        window.app.state = data;
        window.app.agents = data.agents || {};

        dispatch("state:update", data);
        dispatch("agents:update", window.app.agents);
    });

    // ─────────────────────────────
    // 👥 AGENTS SYSTEM
    // ─────────────────────────────
    socketInstance.on("agent_connected", data => {
        console.log("🟢 Agent connected:", data);

        if (!data?.agent_id) return;

        window.app.agents[data.agent_id] = data;

        dispatch("agents:update", window.app.agents);
    });

    socketInstance.on("agent_offline", data => {
        console.log("🔴 Agent offline:", data);

        if (!data?.agent_id) return;

        delete window.app.agents[data.agent_id];

        dispatch("agents:update", window.app.agents);
    });

    socketInstance.on("agents_update", agents => {
        console.log("📡 Agents sync:", agents);

        if (!agents) return;

        window.app.agents = agents;

        dispatch("agents:update", agents);
    });

    // ─────────────────────────────
    // 💻 TERMINAL
    // ─────────────────────────────
    socketInstance.on("terminal_output", data => {
        dispatch("terminal:output", data);
    });

    // ─────────────────────────────
    // 📦 PAYLOAD
    // ─────────────────────────────
    socketInstance.on("payload_generated", payload => {
        dispatch("payload:generated", payload);
    });

    // ─────────────────────────────
    // 📜 LOGS
    // ─────────────────────────────
    socketInstance.on("log", log => {
        dispatch("log:new", log);
    });

    // ─────────────────────────────
    // 📡🔥 NETWORK PIPELINE (CRITICAL FIX)
    // ─────────────────────────────
    socketInstance.on("devices_update", data => {
        console.log("📡 DEVICES UPDATE RECEIVED:", data);

        if (!data || !data.metrics) {
            console.warn("⚠ Invalid devices_update data");
            return;
        }

        window.app.lastUpdate = Date.now();

        dispatch("network:update", data);
    });

    // ─────────────────────────────
    // 🚨 ANOMALY SYSTEM (FIXED EVENT NAME)
    // ─────────────────────────────
    socketInstance.on("network_anomaly", data => {
        console.warn("🚨 ANOMALY DETECTED:", data);

        dispatch("network:anomaly", data); // ✅ FIXED NAME
    });

    // ─────────────────────────────
    // ⚡ AUTO RESPONSE SYSTEM
    // ─────────────────────────────
    socketInstance.on("auto_action", data => {
        console.log("⚡ AUTO ACTION RECEIVED:", data);

        if (!data?.ip) return;

        dispatch("auto:action", data);
    });

    // ─────────────────────────────
    // 🎯 LISTENER STATUS
    // ─────────────────────────────
    socketInstance.on("listener:status", data => {
        console.log("🎯 Listener status:", data);

        dispatch("listener:status", data);
    });

    // ─────────────────────────────
    // ❤️ HEARTBEAT (DEBUG)
    // ─────────────────────────────
    setInterval(() => {
        if (!window.app.connected) {
            console.warn("⚠ Socket not connected");
        }
    }, 5000);

    return socketInstance;
}

// ─────────────────────────────
// 🧠 EVENT DISPATCH HELPER
// ─────────────────────────────
function dispatch(name, detail = {}) {
    document.dispatchEvent(new CustomEvent(name, { detail }));
}
