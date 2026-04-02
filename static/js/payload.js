// static/js/payload.js

export function initPayload() {
    console.log("📦 Payload module initialized");
    waitForElementsAndLoad();
}


// ─────────────────────────────
// WAIT UNTIL DOM ELEMENTS EXIST
// ─────────────────────────────
function waitForElementsAndLoad() {
    const interval = setInterval(() => {
        const loaderSelect = document.getElementById("loaderSelect");
        const certSelect = document.getElementById("certSelect");

        if (loaderSelect && certSelect) {
            clearInterval(interval);
            loadPayloadOptions();
        }
    }, 100);
}


// ─────────────────────────────
// LOAD OPTIONS
// ─────────────────────────────
async function loadPayloadOptions() {
    try {
        const loaderSelect = document.getElementById("loaderSelect");
        const certSelect = document.getElementById("certSelect");

        if (!loaderSelect || !certSelect) return;

        // ───────── LOAD LOADERS ─────────
        console.log("🔄 Fetching loaders...");
        const loaderRes = await fetch("/api/payload/loaders");
        const loaders = await loaderRes.json();

        loaderSelect.innerHTML = "";
        loaderSelect.appendChild(new Option("Select Loader", ""));

        loaders.forEach(l => {
            loaderSelect.appendChild(new Option(l, l));
        });

        // ───────── LOAD CERTS ─────────
        console.log("🔄 Fetching certificates...");
        const certRes = await fetch("/api/payload/certificates");

        if (!certRes.ok) {
            throw new Error("Failed to fetch certs");
        }

        const certs = await certRes.json();

        certSelect.innerHTML = "";
        certSelect.appendChild(new Option("Select Certificate", ""));

        certs.forEach(c => {
            certSelect.appendChild(new Option(c, c));
        });

        console.log("✅ Payload options loaded");

    } catch (err) {
        console.error("❌ Error loading payload options:", err);

        // fallback UI
        const certSelect = document.getElementById("certSelect");
        if (certSelect) {
            certSelect.innerHTML = "<option>Error loading certificates</option>";
        }
    }
}

// ─────────────────────────────
// GENERATE PAYLOAD
// ─────────────────────────────
async function generatePayload() {
    try {
        const loader = document.getElementById("loaderSelect")?.value;
        const cert = document.getElementById("certSelect")?.value;

        if (!loader) {
            alert("Select a loader");
            return;
        }

        console.log("🚀 Generating payload:", loader, cert);

        const res = await fetch("/api/payload/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer dev-token"   // ✅ FIXED
            },
            body: JSON.stringify({
                loader: loader,
                certificate: cert
            })
        });

        if (!res.ok) throw new Error("Payload generation failed");

        const data = await res.json();

        if (data.file) {
            window.location.href = data.file;

            const resultDiv = document.getElementById("payloadResult");
            if (resultDiv) {
                resultDiv.innerHTML = `
                    <div style="margin-top:15px;">
                        <a href="${data.file}" download>
                            <button>Download Payload</button>
                        </a>
                    </div>
                `;
            }
        } else {
            alert(data.error || "Generation failed");
        }

    } catch (err) {
        console.error("❌ Generate error:", err);
        alert("Payload generation failed");
    }
}


// ─────────────────────────────
// GLOBAL
// ─────────────────────────────
window.generatePayload = generatePayload;
window.reloadPayloadOptions = loadPayloadOptions;
