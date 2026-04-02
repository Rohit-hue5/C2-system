// static/js/dashboard.js

let ppsChart = null;
let packetHistory = [];
let timeLabels = [];
let activeAlerts = [];

export function initDashboard() {
    console.log("🚀 [Dashboard] Initializing...");

    initChart();

    // ─────────────────────────────
    // 📡 NETWORK EVENTS (DEBUG ENABLED)
    // ─────────────────────────────
    document.addEventListener("network:update", e => {
        console.log("📊 DASHBOARD RECEIVED:", e.detail); // 🔥 DEBUG

        const data = e.detail;
        if (!data || !data.metrics) {
            console.warn("⚠ Invalid dashboard data");
            return;
        }

        updateMetrics(data.metrics);
        updateDeviceCount(data.metrics.device_count || 0);
        updateChart(data.metrics);

        mergeAlerts(data.alerts || []);
    });

    // ─────────────────────────────
    // 🚨 ANOMALY (FIXED NAME)
    // ─────────────────────────────
    document.addEventListener("network:anomaly", e => {
        console.warn("🚨 Dashboard anomaly:", e.detail);
        showAnomalyBanner(e.detail);
    });

    // ─────────────────────────────
    // ⚡ AUTO RESPONSE
    // ─────────────────────────────
    document.addEventListener("auto:action", e => {
        console.log("⚡ Dashboard auto action:", e.detail);

        const data = e.detail;

        if (!data?.ip) return;

        addAlert({
            ip: data.ip,
            severity: "CRITICAL",
            reason: `⚡ AUTO ACTION → ${data.action}`
        }, true);
    });

    // ─────────────────────────────
    // EXISTING SYSTEM
    // ─────────────────────────────
    document.addEventListener("state:update", e => {
        updateStats(e.detail?.stats);
    });

    document.addEventListener("agents:update", e => {
        updateAgents(e.detail);
    });
}

// ─────────────────────────────
// 📊 INIT CHART
// ─────────────────────────────
function initChart() {
    const ctx = document.getElementById("ppsChart");

    if (!ctx) {
        console.warn("⚠ Chart canvas not found");
        return;
    }

    ppsChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: timeLabels,
            datasets: [{
                label: "Packets/sec",
                data: packetHistory,
                borderWidth: 2,
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            animation: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    console.log("📈 Chart initialized");
}

// ─────────────────────────────
// 📈 UPDATE CHART
// ─────────────────────────────
function updateChart(metrics) {
    if (!ppsChart || !metrics) return;

    const now = new Date().toLocaleTimeString();

    timeLabels.push(now);
    packetHistory.push(metrics.pps || 0);

    if (timeLabels.length > 30) {
        timeLabels.shift();
        packetHistory.shift();
    }

    try {
        ppsChart.update();
    } catch (e) {
        console.warn("⚠ Chart update error:", e);
    }
}

// ─────────────────────────────
// 📊 METRICS
// ─────────────────────────────
function updateMetrics(metrics) {
    const ppsEl = document.getElementById("pps");
    const totalEl = document.getElementById("totalPackets");

    if (ppsEl) ppsEl.innerText = metrics.pps ?? 0;
    if (totalEl) totalEl.innerText = metrics.total_packets ?? 0;
}

// ─────────────────────────────
// 🚨 ALERT SYSTEM
// ─────────────────────────────
function mergeAlerts(newAlerts) {
    newAlerts.forEach(a => {
        const exists = activeAlerts.some(
            x => x.ip === a.ip && x.severity === a.severity
        );

        if (!exists) activeAlerts.push(a);
    });

    renderAlerts();
}

// ─────────────────────────────
// 🔥 RENDER ALERTS
// ─────────────────────────────
function renderAlerts() {
    const container = document.getElementById("alerts");
    if (!container) return;

    container.innerHTML = "";

    if (activeAlerts.length === 0) {
        container.innerHTML = "<p>No threats detected</p>";
        updateAlertCount(0);
        return;
    }

    const priority = { CRITICAL: 3, HIGH: 2, MEDIUM: 1 };

    activeAlerts.sort((a, b) =>
        (priority[b.severity] || 0) - (priority[a.severity] || 0)
    );

    activeAlerts.forEach(a => {
        const div = document.createElement("div");

        let color = "gray";
        if (a.severity === "CRITICAL") color = "red";
        else if (a.severity === "HIGH") color = "orange";
        else if (a.severity === "MEDIUM") color = "yellow";

        div.className = "alert";
        div.style.borderLeft = `4px solid ${color}`;
        div.style.padding = "6px";
        div.style.marginBottom = "5px";

        div.innerHTML = `
            <b>${a.severity}</b> → ${a.ip}<br>
            <small>${a.reason || ""}</small>
        `;

        container.appendChild(div);
    });

    updateAlertCount(activeAlerts.length);
}

// ─────────────────────────────
// ➕ ADD ALERT (REALTIME)
// ─────────────────────────────
function addAlert(a, prepend = true) {
    const exists = activeAlerts.some(
        x => x.ip === a.ip && x.reason === a.reason
    );

    if (!exists) activeAlerts.push(a);

    renderAlerts();
}

// ─────────────────────────────
// 🔢 ALERT COUNT
// ─────────────────────────────
function updateAlertCount(count) {
    const el = document.getElementById("alertCount");
    if (el) el.innerText = count;
}

// ─────────────────────────────
// 🚨 ANOMALY BANNER
// ─────────────────────────────
function showAnomalyBanner(data) {
    let banner = document.getElementById("anomalyBanner");

    if (!banner) {
        banner = document.createElement("div");
        banner.id = "anomalyBanner";

        banner.style.background = "red";
        banner.style.color = "white";
        banner.style.padding = "10px";
        banner.style.marginBottom = "10px";
        banner.style.fontWeight = "bold";

        document.querySelector(".content")?.prepend(banner);
    }

    banner.innerText = `🚨 ANOMALY DETECTED: ${data?.type || "UNKNOWN"}`;

    setTimeout(() => banner.remove(), 5000);
}

// ─────────────────────────────
// 📡 DEVICE COUNT
// ─────────────────────────────
function updateDeviceCount(count) {
    const el = document.getElementById("deviceCount");
    const topEl = document.getElementById("deviceCountTop");

    if (el) el.innerText = count;
    if (topEl) topEl.innerText = count;
}

// ─────────────────────────────
// EXISTING SYSTEM
// ─────────────────────────────
function updateStats(stats) {
    if (!stats) return;

    const scoreEl = document.getElementById("cardScore");

    if (scoreEl && stats.best_score !== undefined) {
        scoreEl.innerText = stats.best_score + "%";
    }
}

function updateAgents(agents) {
    const el = document.getElementById("agentCount");
    if (el && agents) {
        el.innerText = Object.keys(agents).length;
    }
}
