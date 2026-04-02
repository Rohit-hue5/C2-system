export function initSandbox() {

    const btn = document.getElementById("analyze-btn");
    const input = document.getElementById("sandbox-input");
    const logs = document.getElementById("sandbox-logs");
    const resultBox = document.getElementById("sandbox-result");

    // 🚨 IMPORTANT FIX
    if (!btn || !input || !logs || !resultBox) {
        return; // STOP if not on sandbox page
    }

    function log(text) {
        const div = document.createElement("div");
        div.textContent = text;
        logs.appendChild(div);
        logs.scrollTop = logs.scrollHeight;
    }

    function waitSocket() {
        if (!window.socket) {
            setTimeout(waitSocket, 200);
            return;
        }

        const socket = window.socket;

        btn.addEventListener("click", () => {
            const file = input.value.trim();
            if (!file) return;

            logs.innerHTML = "";
            resultBox.innerHTML = "";

            socket.emit("sandbox:analyze", { file });
        });

        socket.on("sandbox:log", (res) => {
            log(res.data);
        });

        socket.on("sandbox:result", (res) => {
            resultBox.innerText = JSON.stringify(res, null, 2);
        });

        console.log("✅ Sandbox ready");
    }

    waitSocket();
}
