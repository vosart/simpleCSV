import { fetchTask, retryTask, deleteTask } from "../api/task.js";

const params = new URLSearchParams(window.location.search);
const file_id = params.get("file_id");

// ===== LOAD =====

async function loadTask() {
    const task = await fetchTask();

    document.getElementById("file_id").innerText = task.file_id;
    document.getElementById("status").innerText = task.status;
    document.getElementById("attempts").innerText = task.attempts;

    document.getElementById("input_path").innerText = task.input_path;
    document.getElementById("output_path").innerText = task.output_path;
}

// ===== EVENTS =====

document.addEventListener("DOMContentLoaded", () => {

    document.getElementById("retryBtn").addEventListener("click", async () => {
        try {
            await retryTask(file_id);
            loadTask();
        } catch (e) {
            console.error(e);
        }
    });

    document.getElementById("deleteBtn").addEventListener("click", async () => {
        const ok = confirm(`Delete task ${file_id}?`);
        if (!ok) return;

        try {
            await deleteTask(file_id);
            window.location.href = "/";
        } catch (e) {
            console.error(e);
            alert("Delete failed");
        }
    });

});

// старт
loadTask();
setInterval(loadTask, 3000);