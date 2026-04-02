// static/js/model.js

// ─────────────────────────────
// 🔗 ELEMENTS
// ─────────────────────────────
const trainBtn = document.getElementById("start-training");
const evalBtn = document.getElementById("start-eval");

const trainStatus = document.getElementById("training-status");
const evalStatus = document.getElementById("evaluation-status");

let pollingInterval = null;
let currentTaskId = null;


// ─────────────────────────────
// 🚀 START TRAINING
// ─────────────────────────────
trainBtn?.addEventListener("click", async () => {
    try {
        setTrainingUI(true);
        updateTrainingStatus("🚀 Initializing training pipeline...");

        const res = await fetch("/api/models/train", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",   // ✅ FIXED
                "Authorization": "Bearer dev-token"
            },
            body: JSON.stringify({
                episodes: 5000
            })
        });

        const data = await res.json();

        if (!res.ok || data.status !== "started") {
            throw new Error(data.message || "Training failed to start");
        }

        updateTrainingStatus("🔥 Training started");

        if (data.task_id) {
            currentTaskId = data.task_id;
            startPolling();
        } else {
            monitorPassiveTraining();
        }

    } catch (err) {
        console.error(err);
        updateTrainingStatus("❌ " + err.message);
        setTrainingUI(false);
    }
});


// ─────────────────────────────
// 🔄 POLLING TRAINING STATUS
// ─────────────────────────────
function startPolling() {
    if (!currentTaskId) return;

    clearInterval(pollingInterval);

    pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`/api/models/status/${currentTaskId}`);
            const data = await res.json();

            renderTrainingStatus(data);

            if (data.status === "completed" || data.status === "failed") {
                clearInterval(pollingInterval);
                setTrainingUI(false);

                updateTrainingStatus(
                    data.status === "completed"
                        ? "✅ Training completed"
                        : "❌ Training failed"
                );
            }

        } catch (err) {
            console.error("Polling error:", err);
        }
    }, 2000);
}


// ─────────────────────────────
// 📊 PASSIVE MONITOR (THREAD MODE)
// ─────────────────────────────
function monitorPassiveTraining() {
    let dots = 0;

    pollingInterval = setInterval(() => {
        dots = (dots + 1) % 4;

        updateTrainingStatus("Training in progress" + ".".repeat(dots));

    }, 1000);

    setTimeout(() => {
        clearInterval(pollingInterval);
        setTrainingUI(false);
        updateTrainingStatus("⚠ Training running in background");
    }, 60000);
}


// ─────────────────────────────
// 📊 RENDER TRAINING STATUS
// ─────────────────────────────
function renderTrainingStatus(data) {
    let text = `Status: ${data.status}`;

    if (data.progress !== undefined) {
        text += ` | ${data.progress}%`;
    }

    if (data.episode !== undefined) {
        text += ` | Episode: ${data.episode}`;
    }

    if (data.reward !== undefined) {
        text += ` | Reward: ${data.reward.toFixed(3)}`;
    }

    updateTrainingStatus(text);
}


// ─────────────────────────────
// 🧪 RUN EVALUATION
// ─────────────────────────────
evalBtn?.addEventListener("click", async () => {
    try {
        setEvaluationUI(true);
        updateEvalStatus("🧪 Running evaluation...");

        const res = await fetch("/api/models/evaluate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",   // ✅ FIXED
                "Authorization": "Bearer dev-token"
            }
        });

        const data = await res.json();

        if (!res.ok || data.status !== "success") {
            throw new Error(data.message || "Evaluation failed");
        }

        const result = data.result || {};
        const score = result.score ?? 0;

        updateEvalStatus(`✅ Score: ${score.toFixed(4)}`);

    } catch (err) {
        console.error(err);
        updateEvalStatus("❌ " + err.message);
    } finally {
        setEvaluationUI(false);
    }
});


// ─────────────────────────────
// 🎛 UI HELPERS
// ─────────────────────────────
function setTrainingUI(isRunning) {
    if (!trainBtn) return;

    trainBtn.disabled = isRunning;
    trainBtn.innerText = isRunning ? "Training..." : "Start Training";
}

function setEvaluationUI(isRunning) {
    if (!evalBtn) return;

    evalBtn.disabled = isRunning;
    evalBtn.innerText = isRunning ? "Evaluating..." : "Run Evaluation";
}

function updateTrainingStatus(msg) {
    if (trainStatus) trainStatus.innerText = msg;
}

function updateEvalStatus(msg) {
    if (evalStatus) evalStatus.innerText = msg;
}
