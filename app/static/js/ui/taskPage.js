import { fetchTask, retryTask, deleteTask } from "../api/task.js";

document.addEventListener("DOMContentLoaded", () => {
    const params = new URLSearchParams(window.location.search);
    const file_id = params.get("file_id");
    if (!file_id) return console.error("No file_id in URL");

    const fileIdEl = document.getElementById("file_id");
    const statusEl = document.getElementById("status");
    const attemptsEl = document.getElementById("attempts");
    const inputPathEl = document.getElementById("input_path");
    const outputPathEl = document.getElementById("output_path");

    const retryBtn = document.getElementById("retryBtn");
    const deleteBtn = document.getElementById("deleteBtn");

    async function loadTask() {
        try {
            const task = await fetchTask(file_id);
            fileIdEl.innerText = task.file_id;
            statusEl.innerText = task.status;
            attemptsEl.innerText = task.attempts;
            inputPathEl.innerText = task.input_path;
            outputPathEl.innerText = task.output_path;

            statusEl.className = "";
            if (task.status === "done") statusEl.classList.add("done");
            else if (task.status === "failed") statusEl.classList.add("failed");
            else if (task.status === "processing") statusEl.classList.add("processing");

        } catch (err) {
            console.error("Failed to load task:", err);
        }
    }

    retryBtn?.addEventListener("click", async () => {
        try {
            await retryTask(file_id);
            await loadTask();
        } catch (err) {
            console.error("Retry failed:", err);
            alert("Retry failed");
        }
    });

    deleteBtn?.addEventListener("click", async () => {
        const ok = confirm(`Delete task ${file_id}?`);
        if (!ok) return;

        try {
            await deleteTask(file_id);
            window.location.href = "/";
        } catch (err) {
            console.error("Delete failed:", err);
            alert("Delete failed");
        }
    });

    loadTask();
    setInterval(loadTask, 3000);
});