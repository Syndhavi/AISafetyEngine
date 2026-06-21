const DB_NAME = "ChatSafetyDB";
const STORE_NAME = "messages";

function initDB() {
    return new Promise((resolve, reject) => {
        let request = indexedDB.open(DB_NAME, 1);

        request.onupgradeneeded = function (e) {
            let db = e.target.result;
            db.createObjectStore(STORE_NAME, { autoIncrement: true });
        };

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function saveMessage(data) {
    let db = await initDB();

    let tx = db.transaction(STORE_NAME, "readwrite");
    let store = tx.objectStore(STORE_NAME);

    store.add({
        ...data,
        timestamp: new Date().toISOString()
    });
}