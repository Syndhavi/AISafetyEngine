document.addEventListener("DOMContentLoaded", () => {

    // 🔹 Load saved emails on popup open
    chrome.storage.local.get(["userEmail", "guardianEmail"], (data) => {
        if (data.userEmail) {
            document.getElementById("userEmail").value = data.userEmail;
        }
        if (data.guardianEmail) {
            document.getElementById("guardianEmail").value = data.guardianEmail;
        }
    });

    // 🔹 Save button
    document.getElementById("saveBtn").addEventListener("click", () => {

        let userEmail = document.getElementById("userEmail").value.trim();
        let guardianEmail = document.getElementById("guardianEmail").value.trim();

        // ✅ Basic validation
        if (!validateEmail(userEmail) || !validateEmail(guardianEmail)) {
            alert("❌ Enter valid email addresses!");
            return;
        }

        chrome.storage.local.set({
            userEmail: userEmail,
            guardianEmail: guardianEmail
        }, () => {
            showStatus("✅ Emails Saved!");
        });

    });

});

// 🔹 Email validation function
function validateEmail(email) {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

// 🔹 Better UI feedback (instead of alert)
function showStatus(message) {
    let status = document.getElementById("status");

    if (status) {
        status.innerText = message;
        status.style.color = "green";

        setTimeout(() => {
            status.innerText = "";
        }, 2000);
    } else {
        alert(message);
    }
}