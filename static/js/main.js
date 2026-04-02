// static/js/main.js

import { initSocket } from "./socket.js";
import { initDashboard } from "./dashboard.js";
import { initPayload } from "./payload.js";
import { initAgents } from "./agents.js";
import { initLogs } from "./logs.js";
import { initTerminal } from "./terminal.js";
import { initSandbox } from "./sandbox.js";

import {
    startListener,
    stopListener
} from "./listener.js";

// model system
import "./model.js";

// ─────────────────────────────
// 🧠 SAFE INIT WRAPPER
// ─────────────────────────────
function safeInit(name, fn) {
    try {
        console.log(`⚙ Initializing ${name}...`);
        fn();
        console.log(`✅ ${name} initialized`);
    } catch (e) {
        console.error(`❌ ${name} failed:`, e);
    }
}

// ─────────────────────────────
// 🚀 APP BOOTSTRAP
// ─────────────────────────────
window.addEventListener("DOMContentLoaded", () => {
    console.log("🚀 [C2] Booting system...");

    // ─────────────────────────────
    // 🔥 INIT SOCKET FIRST (CRITICAL)
    // ─────────────────────────────
    const socket = initSocket();
    window.socket = socket;

    // expose globally for UI buttons
    window.startListener = startListener;
    window.stopListener = stopListener;

    // ─────────────────────────────
    // 🔍 PAGE DETECTION (IMPROVED)
    // ─────────────────────────────

    const hasDashboard = document.getElementById("ppsChart");
    const hasSandbox = document.getElementById("sandbox-input");
    const hasTerminal = document.getElementById("terminal-input");
    const hasPayload = document.getElementById("payload");
    const hasAgents = document.getElementById("agents-container");
    const hasLogs = document.getElementById("logs-container");

    // ─────────────────────────────
    // ⚙ MODULE INIT (SAFE)
    // ─────────────────────────────

    if (hasDashboard) {
        safeInit("Dashboard", initDashboard);
    }

    if (hasSandbox) {
        safeInit("Sandbox", initSandbox);
    }

    if (hasTerminal) {
        safeInit("Terminal", initTerminal);
    }

    if (hasPayload) {
        safeInit("Payload", initPayload);
    }

    if (hasAgents) {
        safeInit("Agents", initAgents);
    }

    if (hasLogs) {
        safeInit("Logs", initLogs);
    }

    // model system detection
    if (
        document.getElementById("start-training") ||
        document.getElementById("start-eval")
    ) {
        console.log("🧠 Model module active");
    }

    // ─────────────────────────────
    // ❤️ SYSTEM HEALTH CHECK
    // ─────────────────────────────
    setTimeout(() => {
        if (!window.app?.connected) {
            console.warn("⚠ Socket not connected after init");
        } else {
            console.log("✅ System fully connected");
        }
    }, 2000);

    console.log("🔥 [C2] System Ready");
});
