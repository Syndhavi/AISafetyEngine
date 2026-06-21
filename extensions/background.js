importScripts("db.js");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {

    fetch("http://127.0.0.1:5001/analyze", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ messages: request.messages })
    })
    .then(res => res.json())
    .then(data => {
        sendResponse({ success: true, data: data }); // ✅ REQUIRED
    })
    .catch(err => {
        console.error("Backend error:", err);
        sendResponse({ success: false }); // ✅ STILL RESPOND
    });

    return true; // keep this
});


// ==============================
// 🚀 PROCESS MESSAGES
// ==============================
async function processMessages(messages) {

    try {
        let res = await fetch("http://127.0.0.1:5001/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ messages })
        });

        let data = await res.json();

        handleActions(data.results);

    } catch (err) {
        console.log("❌ Backend error:", err);
    }
}


// ==============================
// ⚙️ HANDLE ACTIONS
// ==============================
function handleActions(results) {

    results.forEach(async (r) => {

        await saveMessage(r);

        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {

            if (!tabs.length) return;

            chrome.tabs.sendMessage(tabs[0].id, {
                type: "ACTION",
                action: r.action,
                message: r.message
            });
        });

        if (r.action === "ALERT_GUARDIAN") {
            await sendAlertToBackend();
        }
    });
}


// ==============================
// 📧 ALERT API
// ==============================
async function sendAlertToBackend() {

    chrome.storage.local.get(["userEmail", "guardianEmail"], async (data) => {

        if (!data.userEmail || !data.guardianEmail) return;

        try {
            await fetch("http://127.0.0.1:5001/alert", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    user_email: data.userEmail,
                    guardian_email: data.guardianEmail
                })
            });

        } catch (err) {
            console.log("❌ Alert API error:", err);
        }
    });
}