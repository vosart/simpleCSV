export class PaginationController {
    constructor({ tableId, paginationId, fetchUrl, limit = 10 }) {
        this.table = document.getElementById(tableId);
        this.paginationContainer = document.getElementById(paginationId);
        this.fetchUrl = fetchUrl;
        this.limit = limit;
        this.currentPage = 1;

        if (!this.table) {
            throw new Error(`Table not found: ${tableId}`);
        }

        if (!this.paginationContainer) {
            throw new Error(`Pagination container not found: ${paginationId}`);
        }

        this.table.addEventListener("click", (e) => this.handleTableClick(e));
    }

    async handleTableClick(e) {
        const btn = e.target.closest("button");
        if (!btn) return;

        const action = btn.dataset.action;
        const file_id = btn.dataset.id;
        if (!action || !file_id) return;

        try {
            if (action === "retry") {
                await fetch(`/tasks/${file_id}/retry`, { method: "POST" });
                this.loadTasks();
            }

            if (action === "delete") {
                const ok = confirm(`Delete task ${file_id}?`);
                if (!ok) return;

                await fetch(`/tasks/${file_id}`, { method: "DELETE" });
                this.loadTasks();
            }
        } catch (err) {
            console.error("Action failed:", err);
            alert("Action failed");
        }
    }

    async loadTasks() {
        const offset = (this.currentPage - 1) * this.limit;

        const res = await fetch(
            `${this.fetchUrl}?limit=${this.limit}&offset=${offset}`
        );

        const data = await res.json();

        const tasks = data.items || data; // поддержка обоих форматов
        const total = data.total ?? tasks.length;

        this.renderTasks(tasks);
        this.renderPagination(total);
    }

    renderTasks(tasks) {
        this.table.innerHTML = "";

        if (!Array.isArray(tasks) || tasks.length === 0) {
            this.table.innerHTML = `<tr><td colspan="4">No tasks</td></tr>`;
            return;
        }

        tasks.forEach(task => {
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

            this.table.appendChild(row);
        });
    }

    renderPagination(total) {


        const pages = Math.ceil(total / this.limit);

        console.log("TOTAL:", total);
        console.log("PAGES:", pages);

        this.paginationContainer.innerHTML = "";

        if (pages <= 1) return;

        const createBtn = (text, page, disabled = false, active = false) => {
            const btn = document.createElement("button");
            btn.innerText = text;
            btn.disabled = disabled;

            if (active) {
                btn.style.fontWeight = "bold";
                btn.style.textDecoration = "underline";
            }

            btn.addEventListener("click", () => {
                this.currentPage = page;
                this.loadTasks();
            });

            this.paginationContainer.appendChild(btn);
        };

        // Prev
        createBtn("<", Math.max(1, this.currentPage - 1), this.currentPage === 1);

        // Pages (ограничение, чтобы не засорять UI)
        const maxVisible = 7;
        let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
        let end = start + maxVisible - 1;

        if (end > pages) {
            end = pages;
            start = Math.max(1, end - maxVisible + 1);
        }

        for (let i = start; i <= end; i++) {
            createBtn(i, i, false, i === this.currentPage);
        }

        // Next
        createBtn(">", Math.min(pages, this.currentPage + 1), this.currentPage === pages);
    }



    reset() {
        this.currentPage = 1;
        this.loadTasks();
    }
}