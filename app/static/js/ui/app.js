import { PaginationController } from "./pagination.js";

document.addEventListener("DOMContentLoaded", () => {

    const pagination = new PaginationController({
        tableId: "tasksTable",
        paginationId: "pagination",
        fetchUrl: "/tasks",
        limit: 10
    });

    pagination.loadTasks();

    const uploadBtn = document.getElementById("uploadBtn");
    uploadBtn?.addEventListener("click", async () => {
        const fileInput = document.getElementById("fileInput");
        const file = fileInput.files[0];
        if (!file) return alert("Select a file first");

        const formData = new FormData();
        formData.append("file", file);

        try {
            await fetch("/process_csv", { method: "POST", body: formData });
            pagination.reset();
        } catch (err) {
            console.error(err);
            alert("Upload failed");
        }
    });
});