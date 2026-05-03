const params = new URLSearchParams(window.location.search);
const file_id = params.get("file_id");

export async function fetchTask() {
    const res = await fetch(`/tasks/${file_id}`);
    if (!res.ok) throw new Error("Failed to load task");
    return res.json();
}

export async function retryTask(file_id) {
    const res = await fetch(`/tasks/${file_id}/retry`, {
        method: "POST"
    });

    if (!res.ok) throw new Error("Retry failed");
}

export async function deleteTask(file_id) {
    const res = await fetch(`/tasks/${file_id}`, {
        method: "DELETE"
    });

    if (!res.ok) {
        const text = await res.text();
        throw new Error(text || "Delete failed");
    }
}