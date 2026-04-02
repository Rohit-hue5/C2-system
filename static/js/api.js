// static/js/api.js

const BASE = "/api";

export async function apiGet(path) {
    const res = await fetch(BASE + path);
    return res.json();
}

export async function apiPost(path, data) {
    const res = await fetch(BASE + path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });
    return res.json();
}
