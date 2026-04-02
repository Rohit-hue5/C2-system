// static/js/terminal.js

export function initTerminal() {
    const input = document.getElementById("terminal-input");
    const output = document.getElementById("terminal-output");

    let history = [];
    let historyIndex = -1;

    let currentAgent = null;   // 🔥 active agent
    let prompt = "c2>";

    function append(text, type = "normal") {
        const div = document.createElement("div");

        if (type === "error") div.style.color = "red";
        if (type === "success") div.style.color = "lime";

        div.textContent = text;
        output.appendChild(div);
        output.scrollTop = output.scrollHeight;
    }

    function updatePrompt() {
        if (currentAgent) {
            prompt = `agent[${currentAgent}]>`;
        } else {
            prompt = "c2>";
        }

        input.placeholder = prompt;
    }

    function waitForSocket() {
        if (!window.socket) {
            console.log("⏳ Waiting for socket (terminal)...");
            setTimeout(waitForSocket, 200);
            return;
        }

        const socket = window.socket;
        console.log("✅ Terminal ready");

        // ─────────────────────────────
        // ⌨ INPUT HANDLER
        // ─────────────────────────────
        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                const cmd = input.value.trim();
                if (!cmd) return;

                append(`${prompt} ${cmd}`, "success");

                history.push(cmd);
                historyIndex = history.length;

                handleCommand(cmd, socket);

                input.value = "";
            }

            // 🔼 HISTORY UP
            if (e.key === "ArrowUp") {
                if (historyIndex > 0) {
                    historyIndex--;
                    input.value = history[historyIndex];
                }
            }

            // 🔽 HISTORY DOWN
            if (e.key === "ArrowDown") {
                if (historyIndex < history.length - 1) {
                    historyIndex++;
                    input.value = history[historyIndex];
                } else {
                    input.value = "";
                }
            }
        });

        // ─────────────────────────────
        // 📥 OUTPUT HANDLER
        // ─────────────────────────────
        socket.on("terminal_output", (res) => {
            if (!res) return;

            // 🔥 NEW FORMAT SUPPORT
            if (res.output) {
                append(`[${res.agent_id}] ${res.output}`);
            } else if (res.data) {
                append(res.data);
            }
        });

        // ─────────────────────────────
        // 🔌 AGENT CONNECT/DISCONNECT
        // ─────────────────────────────
        socket.on("agent_connected", (data) => {
            append(`🟢 Agent connected: ${data.agent_id}`, "success");
        });

        socket.on("agent_offline", (data) => {
            append(`🔴 Agent offline: ${data.agent_id}`, "error");

            if (currentAgent === data.agent_id) {
                currentAgent = null;
                updatePrompt();
            }
        });

        updatePrompt();
    }

    // ─────────────────────────────
    // 🧠 COMMAND PARSER (C2 CORE)
    // ─────────────────────────────
    function handleCommand(cmd, socket) {
        const parts = cmd.split(" ");

        // 🔥 USE AGENT
        if (parts[0] === "use") {
            if (!parts[1]) {
                append("Usage: use <agent_id>", "error");
                return;
            }

            currentAgent = parts[1];
            append(`🎯 Selected agent: ${currentAgent}`, "success");
            updatePrompt();
            return;
        }

        // 🔥 BACK TO C2 MODE
        if (cmd === "back") {
            currentAgent = null;
            append("↩ Back to C2 mode");
            updatePrompt();
            return;
        }

        // 🔥 LIST AGENTS
        if (cmd === "agents") {
            socket.emit("get_agents");
            return;
        }

        // 🔥 CLEAR
        if (cmd === "clear") {
            output.innerHTML = "";
            return;
        }

        // 🔥 NO AGENT SELECTED
        if (!currentAgent) {
            append("❌ No agent selected. Use: use <agent_id>", "error");
            return;
        }

        // ─────────────────────────────
        // 🚀 SEND COMMAND TO AGENT
        // ─────────────────────────────
        socket.emit("agent_command", {
            agent_id: currentAgent,
            command: cmd
        });
    }

    waitForSocket();
}
