let lockOverlay = null;
let messageInterval = null;
let statusInterval = null;
let isExtensionDead = false;

console.log("🚀 Content script loaded");


// ==============================
// 📩 EXTRACT MESSAGES
// ==============================
async function extractMessages() {
    try {
        const messages = getMessages();

        const response = await new Promise((resolve) => {
            chrome.runtime.sendMessage(
                { messages },
                (res) => resolve(res)
            );
        });

        console.log("📩 Response:", response);

    } catch (err) {
        console.error("💀 Error:", err);
    }
}


// ==============================
// 🧠 SAFE MESSAGE SENDER
// ==============================
chrome.runtime.sendMessage(
    { messages: messages },
    (response) => {
        if (chrome.runtime.lastError) {
            console.warn("⚠️ Runtime error:", chrome.runtime.lastError.message);
            return;
        }

        if (response && response.success) {
            console.log("✅ Backend response:", response.data);
        }
    }
);


// ==============================
// 💀 HANDLE EXTENSION RELOAD
// ==============================
function handleContextInvalid() {

    if (isExtensionDead) return;

    isExtensionDead = true;

    console.log("💀 Extension context lost. Stopping execution...");

    if (messageInterval) clearInterval(messageInterval);
    if (statusInterval) clearInterval(statusInterval);

    // ❌ REMOVE AUTO RELOAD
}


// ==============================
// ⏱ SEND TO BACKEND (FIXED)
// ==============================
setTimeout(() => {

    messageInterval = setInterval(() => {

        if (isExtensionDead) return;

        let messages = extractMessages();
        console.log("📩 Extracted:", messages);

        safeSendMessage({
            type: "MESSAGES",
            data: messages
        });

    }, 5000);

}, 4000);


// ==============================
// 📥 RECEIVE ACTIONS
// ==============================
chrome.runtime.onMessage.addListener((msg) => {

    if (isExtensionDead) return;

    if (msg.type === "ACTION") {

        console.log("📥 Received action:", msg);

        if (msg.action === "WARN") {
            showWarning("⚠️ Suspicious message detected!");
        }

        if (msg.action === "BLOCK") {
            showWarning("🚫 Message Blocked!");
            setLock("BLOCK", 2 * 60 * 1000);
        }

        if (msg.action === "ALERT_GUARDIAN") {
            showWarning("🚨 Guardian Alert!");
            setLock("ALERT_GUARDIAN");
        }
    }
});


// ==============================
// 🔒 APPLY LOCK UI
// ==============================
function applyLock(type) {

    if (lockOverlay) return;

    lockOverlay = document.createElement("div");

    lockOverlay.style.position = "fixed";
    lockOverlay.style.top = "0";
    lockOverlay.style.left = "0";
    lockOverlay.style.width = "100%";
    lockOverlay.style.height = "100%";
    lockOverlay.style.background = "rgba(0,0,0,0.9)";
    lockOverlay.style.color = "white";
    lockOverlay.style.display = "flex";
    lockOverlay.style.justifyContent = "center";
    lockOverlay.style.alignItems = "center";
    lockOverlay.style.fontSize = "24px";
    lockOverlay.style.zIndex = "999999";

    if (type === "BLOCK") {
        lockOverlay.innerText = "🚫 Chat blocked temporarily";
    }

    if (type === "ALERT_GUARDIAN") {
        lockOverlay.innerText = "🚨 Guardian Alert - Access Disabled";
    }

    document.body.appendChild(lockOverlay);
}


// ==============================
// 🔐 SET LOCK
// ==============================
function setLock(type, duration = null) {

    let unlockTime = duration ? Date.now() + duration : null;

    chrome.storage.local.set({
        lockType: type,
        unlockTime: unlockTime
    });

    applyLock(type);
}


// ==============================
// 🔓 CHECK UNLOCK
// ==============================
function checkUnlock() {

    chrome.storage.local.get(["lockType", "unlockTime"], (data) => {

        if (!data.lockType) return;

        if (data.lockType === "BLOCK") {

            if (Date.now() > data.unlockTime) {
                unlockUI();
            } else {
                applyLock("BLOCK");
            }
        }

        if (data.lockType === "ALERT_GUARDIAN") {
            applyLock("ALERT_GUARDIAN");
        }
    });
}


// ==============================
// ✅ UNLOCK UI
// ==============================
function unlockUI() {

    if (lockOverlay) {
        lockOverlay.remove();
        lockOverlay = null;
    }

    chrome.storage.local.clear();

    showWarning("✅ Chat Unlocked");
}


// ==============================
// ⚠️ POPUP UI
// ==============================
function showWarning(text) {

    let div = document.createElement("div");

    div.innerText = text;
    div.style.position = "fixed";
    div.style.top = "20px";
    div.style.right = "20px";
    div.style.background = "red";
    div.style.color = "white";
    div.style.padding = "10px";
    div.style.zIndex = 9999;

    document.body.appendChild(div);

    setTimeout(() => div.remove(), 3000);
}


// ==============================
// 🌐 BACKEND STATUS CHECK
// ==============================
function checkBackendStatus() {

    safeSendMessage(
        { type: "CHECK_STATUS" },
        (response) => {

            if (!response || response.error) {
                console.log("⚠️ Backend not reachable");
                return;
            }

            if (!response.locked) {
                unlockUI();
            } else {
                applyLock(
                    response.type === "ALERT"
                        ? "ALERT_GUARDIAN"
                        : "BLOCK"
                );
            }
        }
    );
}

// ==============================
// 🔁 AUTO CHECK (FIXED)
// ==============================
statusInterval = setInterval(() => {

    if (isExtensionDead) return;

    checkUnlock();
    checkBackendStatus();

}, 5000);


// ==============================
// 🚀 INITIAL RUN
// ==============================
checkUnlock();
checkBackendStatus();