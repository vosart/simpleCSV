import { PaginationController } from "./pagination.js";

async function loadStats() {

    const res = await fetch("/tasks/stats");

    console.log("STATUS:", res.status);

    const data = await res.json();

    console.log("STATS DATA:", data);

    document.getElementById("stats-total").innerText =
        data.total ?? 0;

    document.getElementById("stats-done").innerText =
        data.stats.done ?? 0;

    document.getElementById("stats-failed").innerText =
        data.stats.failed ?? 0;

    document.getElementById("stats-processing").innerText =
        data.stats.processing ?? 0;
}

document.addEventListener("DOMContentLoaded", async () => {

    const pagination = new PaginationController({
        tableId: "tasksTable",
        paginationId: "pagination",
        fetchUrl: "/tasks",
        limit: 10,

        onDataChanged: loadStats
    });

    await pagination.loadTasks();
    await loadStats();

    const uploadBtn = document.getElementById("uploadBtn");

    uploadBtn?.addEventListener("click", async () => {

        const fileInput = document.getElementById("fileInput");
        const file = fileInput.files[0];

        if (!file) {
            alert("Select a file first");
            return;
        }

        const formData = new FormData();
        formData.append("file", file);

        try {

            await fetch("/process_csv", {
                method: "POST",
                body: formData
            });

            await pagination.reset();
            await loadStats();

        } catch (err) {

            console.error(err);
            alert("Upload failed");
        }
    });
});