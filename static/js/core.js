// static/js/core.js

import { initSocket } from "./socket.js";
import { initDashboard } from "./dashboard.js";
import { initPayload } from "./payload.js";
import { initListener } from "./listener.js";

window.app = {
    state: {},
};

window.showPage = function(page) {
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.getElementById("page-" + page).classList.add("active");

    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));
    event.target.closest(".nav-item").classList.add("active");
};

window.addEventListener("DOMContentLoaded", () => {
    initSocket();
    initDashboard();
    initPayload();
    initListener();
    initTerminal();
});
