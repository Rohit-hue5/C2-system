// static/js/agents.js

export function initAgents() {
    document.addEventListener("agents:update", e => {
        renderAgents(e.detail);
    });
}

function renderAgents(agents) {
    const container = document.getElementById("agents-list");

    if (!container) return;

    container.innerHTML = "";

    agents.forEach(agent => {
        const el = document.createElement("div");

        el.className = "agent-card";
        el.innerHTML = `
            <div><b>ID:</b> ${agent.id}</div>
            <div><b>IP:</b> ${agent.ip || "unknown"}</div>
            <div><b>Status:</b> ${agent.status}</div>
        `;

        container.appendChild(el);
    });
}
