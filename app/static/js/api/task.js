export async function fetchTask(file_id) {
    const res = await fetch(`/tasks/${file_id}`);
    if (!res.ok) throw new Error(`Failed to fetch task ${file_id}`);
    return res.json();
}

export async function retryTask(file_id) {
    const res = await fetch(`/tasks/${file_id}/retry`, { method: "POST" });
    if (!res.ok) throw new Error(`Failed to retry task ${file_id}`);
}

export async function deleteTask(file_id) {
    const res = await fetch(`/tasks/${file_id}`, { method: "DELETE" });
    if (!res.ok) throw new Error(`Failed to delete task ${file_id}`);
}