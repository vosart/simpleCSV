const params = new URLSearchParams(window.location.search);
const file_id = params.get("file_id");

async function loadTask() {
    const res = await fetch(`/tasks/${file_id}`);
    const task = await res.json();

    document.getElementById("file_id").innerText = task.file_id;
    document.getElementById("status").innerText = task.status;
    document.getElementById("attempts").innerText = task.attempts;

    document.getElementById("input_path").innerText = task.input_path;
    document.getElementById("output_path").innerText = task.output_path;
}

async function retryTask() {
    await fetch(`/tasks/${file_id}/retry`, { method: "POST" });
    loadTask();
}

async function deleteTask() {
    await fetch(`/tasks/${file_id}`, { method: "DELETE" });
    window.location.href = "/";
}

loadTask();
setInterval(loadTask, 3000);