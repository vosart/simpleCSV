async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    const formData = new FormData();
    formData.append("file", file);

    await fetch("/process_csv", {
        method: "POST",
        body: formData
    });

    loadTasks();
}

async function loadTasks() {
    const res = await fetch("/tasks/all");
    const data = await res.json();

    if (!data.tasks) {
        console.error("Invalid API response", data);
        return;
    }

    const tasks = data.tasks;


    const table = document.getElementById("tasksTable");
    table.innerHTML = "";

    tasks.forEach(task => {
        const row = document.createElement("tr");

        row.innerHTML = `
            <td>${task.file_id}</td>
            <td>${task.status}</td>
            <td>${task.attempts}</td>
            <td>
                <button onclick="retryTask('${task.file_id}')">Retry</button>
                <button onclick="deleteTask('${task.file_id}')">Delete</button>
            </td>
        `;

        table.appendChild(row);
    });
}

async function retryTask(file_id) {
    await fetch(`/tasks/${file_id}/retry`, {
        method: "POST"
    });

    loadTasks();
}
async function deleteTask(file_id) {
    await fetch(`/tasks/${file_id}`, {
        method: "DELETE"
    });

    loadTasks();
}