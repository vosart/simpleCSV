import { fetchTask, retryTask, deleteTask } from "../api/task.js";

async function loadTask() {
    const task = await fetchTask();

    document.getElementById("file_id").innerText = task.file_id;
    document.getElementById("status").innerText = task.status;
    document.getElementById("attempts").innerText = task.attempts;

    document.getElementById("input_path").innerText = task.input_path;
    document.getElementById("output_path").innerText = task.output_path;
}

document.addEventListener("DOMContentLoaded", () => {
    const retryBtn = document.getElementById("retryBtn");
    const deleteBtn = document.getElementById("deleteBtn");

    if (retryBtn) {
        retryBtn.addEventListener("click", async () => {
            const file_id = document.getElementById("file_id").innerText;

            try {
                await retryTask(file_id);
                loadTask();
            } catch (e) {
                console.error(e);
            }
        });
    }

    if (deleteBtn) {
        deleteBtn.addEventListener("click", async () => {
            const file_id = document.getElementById("file_id").innerText;

            const ok = confirm(`Delete task ${file_id}?`);
            if (!ok) return;

            try {
                await deleteTask(file_id);
                loadTask();
            } catch (e) {
                console.error(e);
                alert("Delete failed");
            }
        });
    }
});

document.getElementById("tasksTable").addEventListener("click", async (e) => {
    const btn = e.target.closest("button");
    if (!btn) return;

    const action = btn.dataset.action;
    const file_id = btn.dataset.id;

    if (!action || !file_id) return;

    try {
        if (action === "retry") {
            await retryTask(file_id);
            loadTasks();
        }

        if (action === "delete") {
            const ok = confirm(`Delete task ${file_id}?`);
            if (!ok) return;

            await deleteTask(file_id);
            loadTasks();
        }
    } catch (err) {
        console.error(err);
        alert("Action failed");
    }
});

async function loadTasks() {
    const res = await fetch("/tasks/all");
    const data = await res.json();

    const table = document.getElementById("tasksTable");
    table.innerHTML = "";

    data.tasks.forEach(task => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${task.file_id}</td>
            <td>${task.status}</td>
            <td>${task.attempts}</td>
            <td>
                <button data-action="retry" data-id="${task.file_id}">Retry</button>
                <button data-action="delete" data-id="${task.file_id}">Delete</button>
            </td>
        `;

        table.appendChild(row);
    });
}

document.getElementById("uploadBtn")?.addEventListener("click", async () => {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    await fetch("/process_csv", {
        method: "POST",
        body: formData
    });

    loadTasks();
});

document.addEventListener("DOMContentLoaded", () => {
    loadTasks();
});