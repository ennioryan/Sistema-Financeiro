// Global state
let chartInstance = null;
let allCategories = [];
let currentTransactions = [];

// DOM Loaded Initialization
document.addEventListener("DOMContentLoaded", () => {
    // Set current month and year in inputs
    const now = new Date();
    document.getElementById("filter-month").value = now.getMonth() + 1;
    document.getElementById("filter-year").value = now.getFullYear();
    
    // Set default transaction date to today
    const dateInput = document.getElementById("tx-data");
    const today = now.toISOString().split('T')[0];
    dateInput.value = today;
    dateInput.max = today;

    // Load initial data
    loadCategories().then(() => {
        loadDashboardData();
    });
    loadGoals();

    // Event listeners
    document.getElementById("filter-month").addEventListener("change", loadDashboardData);
    document.getElementById("filter-year").addEventListener("change", loadDashboardData);
});

// Toast notifications helper
function showToast(message, type = "success") {
    const container = document.getElementById("toast-container");
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    
    let iconClass = type === "success" ? "fa-circle-check" : "fa-circle-exclamation";
    
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.75rem;">
            <i class="fa-solid ${iconClass}" style="color: ${type === 'success' ? 'var(--success)' : 'var(--danger)'}"></i>
            <span>${message}</span>
        </div>
        <button onclick="this.parentElement.remove()" style="background:transparent; border:none; color:var(--text-muted); cursor:pointer;">
            <i class="fa-solid fa-xmark"></i>
        </button>
    `;
    
    container.appendChild(toast);
    setTimeout(() => {
        toast.remove();
    }, 4000);
}

// Switch between forms tabs
function switchTab(tabId) {
    const tabs = document.querySelectorAll(".tab-content");
    const buttons = document.querySelectorAll(".tab-btn");
    
    tabs.forEach(tab => tab.style.display = "none");
    buttons.forEach(btn => btn.classList.remove("active"));
    
    document.getElementById(tabId).style.display = "block";
    event.target.classList.add("active");
}

// Modal controls
function openNewGoalModal() {
    document.getElementById("modal-goal").style.display = "flex";
}

function openProgressModal(id, name) {
    document.getElementById("progress-meta-id").value = id;
    document.getElementById("progress-modal-title").innerText = `Lançar progresso em "${name}"`;
    document.getElementById("progress-valor").value = "";
    document.getElementById("modal-progress").style.display = "flex";
}

function closeModal(id) {
    document.getElementById(id).style.display = "none";
}

// Close modals when clicking outside
window.onclick = function(event) {
    const modalGoal = document.getElementById("modal-goal");
    const modalProgress = document.getElementById("modal-progress");
    const modalEditTx = document.getElementById("modal-edit-transaction");
    if (event.target === modalGoal) closeModal("modal-goal");
    if (event.target === modalProgress) closeModal("modal-progress");
    if (event.target === modalEditTx) closeModal("modal-edit-transaction");
}

// Fetch categories from API
async function loadCategories() {
    try {
        const response = await fetch("/api/categorias");
        if (!response.ok) throw new Error("Erro ao buscar categorias");
        allCategories = await response.json();
        loadCategoriesForSelect();
    } catch (error) {
        showToast(error.message, "error");
    }
}

// Populate the categories select box based on transaction type (receita/despesa)
function loadCategoriesForSelect() {
    const txTipo = document.getElementById("tx-tipo").value;
    const select = document.getElementById("tx-categoria");
    select.innerHTML = "";

    const filtered = allCategories.filter(cat => cat.tipo === txTipo);

    if (filtered.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.innerText = "Nenhuma categoria cadastrada";
        select.appendChild(opt);
    } else {
        filtered.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat.id;
            opt.innerText = cat.nome;
            select.appendChild(opt);
        });
    }
}

// Load and render all components for the active period
async function loadDashboardData() {
    const mes = document.getElementById("filter-month").value;
    const ano = document.getElementById("filter-year").value;
    
    showSummaryLoading();
    showTableLoading();
    showChartLoading();
    hideChartError();
    hideTableError();
    
    // 1. Fetch Summary
    try {
        const resSummary = await fetch(`/api/transacoes/resumo?mes=${mes}&ano=${ano}`);
        if (!resSummary.ok) throw new Error("Não foi possível conectar ao servidor.");
        const summary = await resSummary.json();
        
        document.getElementById("summary-receitas").innerText = formatCurrency(summary.receitas);
        document.getElementById("summary-despesas").innerText = formatCurrency(summary.despesas);
        document.getElementById("summary-saldo").innerText = formatCurrency(summary.saldo);
        
        // Dynamic colors for balance card based on value
        const saldoCard = document.querySelector(".card-saldo");
        if (summary.saldo < 0) {
            saldoCard.style.borderColor = "var(--danger)";
        } else {
            saldoCard.style.borderColor = "var(--card-border)";
        }
    } catch (error) {
        console.error("Erro ao carregar resumo:", error);
        document.getElementById("summary-receitas").innerText = "R$ --";
        document.getElementById("summary-despesas").innerText = "R$ --";
        document.getElementById("summary-saldo").innerText = "R$ --";
        showToast("Falha ao sincronizar resumo mensal. O servidor pode estar offline.", "error");
    }

    // 2. Fetch Transactions for table and charts
    try {
        const resTx = await fetch(`/api/transacoes?mes=${mes}&ano=${ano}`);
        if (!resTx.ok) throw new Error("Conexão recusada pelo servidor.");
        const transactions = await resTx.json();
        currentTransactions = transactions; // Guardar transações no estado global
        
        hideChartLoading();
        renderTransactionsTable(transactions);
        renderChart(transactions);
    } catch (error) {
        console.error("Erro ao carregar transacoes:", error);
        hideChartLoading();
        showTableError("Falha de Comunicação", "Não foi possível carregar as transações deste período. Verifique se o servidor está ativo.");
        showChartError("Falha de Comunicação", "Não foi possível gerar o gráfico de despesas.");
    }
}

// Format number to R$ string
function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(value);
}

// Format date to local standard DD/MM/YYYY
function formatDate(dateStr) {
    if (!dateStr) return "";
    const parts = dateStr.split("-");
    if (parts.length !== 3) return dateStr;
    return `${parts[2]}/${parts[1]}/${parts[0]}`;
}

// Render the transactions table
function renderTransactionsTable(transactions) {
    const tbody = document.getElementById("transactions-table-body");
    const emptyState = document.getElementById("table-empty-state");
    tbody.innerHTML = "";

    if (transactions.length === 0) {
        emptyState.style.display = "flex";
        return;
    }
    emptyState.style.display = "none";

    transactions.forEach(t => {
        const tr = document.createElement("tr");
        const catName = t.categoria ? t.categoria.nome : '<span style="color:var(--text-muted)">Sem Categoria</span>';
        const typeClass = t.tipo === "receita" ? "type-receita" : "type-despesa";
        const valPrefix = t.tipo === "receita" ? "+" : "-";

        tr.innerHTML = `
            <td style="font-weight: 500;">${t.descricao}</td>
            <td>${catName}</td>
            <td style="color: var(--text-secondary);">${formatDate(t.data)}</td>
            <td class="${typeClass}">${valPrefix} ${formatCurrency(t.valor)}</td>
            <td>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="delete-btn" onclick="openEditTransactionModal(${t.id})" title="Editar Lançamento" style="color: var(--primary);">
                        <i class="fa-solid fa-pen-to-square"></i>
                    </button>
                    <button class="delete-btn" onclick="handleDeleteTransaction(${t.id})" title="Excluir Lançamento">
                        <i class="fa-solid fa-trash-can"></i>
                    </button>
                </div>
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Render dynamic expenses by category chart using Chart.js
function renderChart(transactions) {
    const canvas = document.getElementById("chartCategorias");
    const emptyState = document.getElementById("chart-empty-state");

    // Aggregate expenses by category
    const expenses = transactions.filter(t => t.tipo === "despesa");
    
    if (expenses.length === 0) {
        canvas.style.display = "none";
        emptyState.style.display = "flex";
        if (chartInstance) {
            chartInstance.destroy();
            chartInstance = null;
        }
        return;
    }

    canvas.style.display = "block";
    emptyState.style.display = "none";

    const dataMap = {};
    expenses.forEach(t => {
        const catName = t.categoria ? t.categoria.nome : "Sem Categoria";
        dataMap[catName] = (dataMap[catName] || 0) + t.valor;
    });

    const labels = Object.keys(dataMap);
    const dataValues = Object.values(dataMap);

    const colors = [
        '#6366f1', '#10b981', '#f43f5e', '#8b5cf6', 
        '#f59e0b', '#06b6d4', '#ec4899', '#14b8a6', 
        '#a855f7', '#3b82f6'
    ];

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(canvas, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: dataValues,
                backgroundColor: colors.slice(0, labels.length),
                borderWidth: 1,
                borderColor: 'rgba(255, 255, 255, 0.1)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        color: '#94a3b8',
                        font: {
                            family: 'Inter',
                            size: 11
                        },
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return ` ${context.label}: ${formatCurrency(context.raw)}`;
                        }
                    }
                }
            },
            cutout: '65%'
        }
    });
}

// Load and render goals
async function loadGoals() {
    const container = document.getElementById("goals-container");
    showGoalsLoading();

    try {
        const response = await fetch("/api/metas");
        if (!response.ok) throw new Error("Não foi possível conectar ao servidor.");
        const goals = await response.json();

        container.innerHTML = "";

        if (goals.length === 0) {
            container.innerHTML = `
                <div class="empty-state" style="padding: 1.5rem 0;">
                    <i class="fa-solid fa-bullseye empty-state-icon" style="font-size: 2rem;"></i>
                    <p style="font-size: 0.85rem;">Nenhuma meta financeira cadastrada.</p>
                </div>
            `;
            return;
        }

        goals.forEach(m => {
            const pct = m.valor_alvo > 0 ? Math.min(100, Math.max(0, (m.valor_atual / m.valor_alvo) * 100)) : 0;
            const progressColor = pct >= 100 ? "var(--success)" : "var(--purple)";

            const card = document.createElement("div");
            card.className = "goal-card";
            card.innerHTML = `
                <div class="goal-info">
                    <div class="goal-name">
                        <h4>${m.nome}</h4>
                        ${m.prazo ? `<div class="deadline"><i class="fa-regular fa-calendar-days"></i> Prazo: ${formatDate(m.prazo)}</div>` : ''}
                    </div>
                    <div class="goal-values">
                        <span class="current">${formatCurrency(m.valor_atual)}</span> 
                        <span style="color: var(--text-muted)">/ ${formatCurrency(m.valor_alvo)}</span>
                    </div>
                </div>
                <div class="goal-progress-container">
                    <div class="goal-bar-bg">
                        <div class="goal-bar-fill" style="width: ${pct}%; background: ${pct >= 100 ? 'var(--success-gradient)' : 'var(--purple-gradient)'}"></div>
                    </div>
                    <div class="goal-pct" style="color: ${progressColor}">${pct.toFixed(0)}%</div>
                </div>
                <div class="goal-actions">
                    <button class="btn btn-mini" onclick="openProgressModal(${m.id}, '${m.nome}')">
                        <i class="fa-solid fa-coins"></i> Lançar Progresso
                    </button>
                </div>
            `;
            container.appendChild(card);
        });
    } catch (error) {
        console.error("Erro ao carregar metas:", error);
        showGoalsError("Falha de Comunicação", "Não foi possível carregar as metas de economia.");
    }
}

// Form Handlers
async function handleNewTransaction(event) {
    event.preventDefault();
    
    const desc = document.getElementById("tx-desc").value;
    const valor = parseFloat(document.getElementById("tx-valor").value);
    const tipo = document.getElementById("tx-tipo").value;
    const catId = parseInt(document.getElementById("tx-categoria").value);
    const dataStr = document.getElementById("tx-data").value;

    if (!catId) {
        showToast("Selecione uma categoria válida para a transação.", "error");
        return;
    }

    const payload = {
        descricao: desc,
        valor: valor,
        tipo: tipo,
        categoria_id: catId,
        data: dataStr || null
    };

    try {
        const response = await fetch("/api/transacoes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao salvar transação");
        }

        showToast("Transação registrada com sucesso!");
        document.getElementById("form-transacao").reset();
        
        // Reset defaults
        document.getElementById("tx-data").value = new Date().toISOString().split('T')[0];
        document.getElementById("tx-tipo").value = tipo; // Keep chosen type
        loadCategoriesForSelect();

        loadDashboardData();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function handleNewCategory(event) {
    event.preventDefault();

    const nome = document.getElementById("cat-nome").value;
    const tipo = document.getElementById("cat-tipo").value;

    const payload = {
        nome: nome,
        tipo: tipo
    };

    try {
        const response = await fetch("/api/categorias", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao criar categoria");
        }

        showToast("Categoria criada com sucesso!");
        document.getElementById("form-categoria").reset();
        
        await loadCategories(); // Refresh list and dropdowns
        loadDashboardData();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function handleNewGoal(event) {
    event.preventDefault();

    const nome = document.getElementById("meta-nome").value;
    const valorAlvo = parseFloat(document.getElementById("meta-alvo").value);
    const prazo = document.getElementById("meta-prazo").value || null;

    const payload = {
        nome: nome,
        valor_alvo: valorAlvo,
        prazo: prazo
    };

    try {
        const response = await fetch("/api/metas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao criar meta");
        }

        showToast("Meta criada com sucesso!");
        closeModal("modal-goal");
        document.getElementById("form-meta").reset();
        loadGoals();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function handleGoalProgress(event) {
    event.preventDefault();

    const id = document.getElementById("progress-meta-id").value;
    const valor = parseFloat(document.getElementById("progress-valor").value);

    const payload = {
        valor: valor
    };

    try {
        const response = await fetch(`/api/metas/${id}/progresso`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao atualizar progresso");
        }

        showToast("Progresso da meta atualizado!");
        closeModal("modal-progress");
        loadGoals();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function handleDeleteTransaction(id) {
    if (!confirm("Deseja realmente excluir esta transação?")) return;

    try {
        const response = await fetch(`/api/transacoes/${id}`, {
            method: "DELETE"
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao excluir transação");
        }

        showToast("Transação excluída!");
        loadDashboardData();
    } catch (error) {
        showToast(error.message, "error");
    }
}

// Abrir modal de edição de transações preenchido
function openEditTransactionModal(id) {
    const tx = currentTransactions.find(t => t.id === id);
    if (!tx) return;
    
    document.getElementById("edit-tx-id").value = tx.id;
    document.getElementById("edit-tx-desc").value = tx.descricao;
    document.getElementById("edit-tx-valor").value = tx.valor;
    document.getElementById("edit-tx-tipo").value = tx.tipo;
    document.getElementById("edit-tx-data").value = tx.data;
    
    // Popular o select de categorias no modal de edição
    loadCategoriesForEditSelect(tx.categoria_id);
    
    document.getElementById("modal-edit-transaction").style.display = "flex";
}

// Popular select de categorias no modal de edição
function loadCategoriesForEditSelect(selectedCatId = null) {
    const txTipo = document.getElementById("edit-tx-tipo").value;
    const select = document.getElementById("edit-tx-categoria");
    select.innerHTML = "";

    const filtered = allCategories.filter(cat => cat.tipo === txTipo);

    if (filtered.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.innerText = "Nenhuma categoria cadastrada";
        select.appendChild(opt);
    } else {
        filtered.forEach(cat => {
            const opt = document.createElement("option");
            opt.value = cat.id;
            opt.innerText = cat.nome;
            if (selectedCatId && cat.id === selectedCatId) {
                opt.selected = true;
            }
            select.appendChild(opt);
        });
    }
}

// Enviar alteração de transação via PUT API
async function handleEditTransaction(event) {
    event.preventDefault();
    
    const id = document.getElementById("edit-tx-id").value;
    const desc = document.getElementById("edit-tx-desc").value;
    const valor = parseFloat(document.getElementById("edit-tx-valor").value);
    const tipo = document.getElementById("edit-tx-tipo").value;
    const catId = parseInt(document.getElementById("edit-tx-categoria").value);
    const dataStr = document.getElementById("edit-tx-data").value;

    if (!catId) {
        showToast("Selecione uma categoria válida para a transação.", "error");
        return;
    }

    const payload = {
        descricao: desc,
        valor: valor,
        tipo: tipo,
        categoria_id: catId,
        data: dataStr || null
    };

    try {
        const response = await fetch(`/api/transacoes/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Erro ao salvar alterações da transação");
        }

        showToast("Transação atualizada com sucesso!");
        closeModal("modal-edit-transaction");
        loadDashboardData();
    } catch (error) {
        showToast(error.message, "error");
    }
}

// Helpers para Loading Skeletons e Spinners

function showSummaryLoading() {
    document.getElementById("summary-receitas").innerHTML = '<div class="skeleton skeleton-value"></div>';
    document.getElementById("summary-despesas").innerHTML = '<div class="skeleton skeleton-value"></div>';
    document.getElementById("summary-saldo").innerHTML = '<div class="skeleton skeleton-value"></div>';
}

function showTableLoading() {
    const tbody = document.getElementById("transactions-table-body");
    document.getElementById("table-empty-state").style.display = "none";
    tbody.innerHTML = `
        <tr><td colspan="5"><div class="skeleton skeleton-text" style="height: 1rem;"></div></td></tr>
        <tr><td colspan="5"><div class="skeleton skeleton-text" style="height: 1rem;"></div></td></tr>
        <tr><td colspan="5"><div class="skeleton skeleton-text" style="height: 1rem;"></div></td></tr>
    `;
}

function showChartLoading() {
    const canvas = document.getElementById("chartCategorias");
    const emptyState = document.getElementById("chart-empty-state");
    canvas.style.display = "none";
    emptyState.style.display = "none";
    
    let spinner = document.getElementById("chart-spinner");
    if (!spinner) {
        spinner = document.createElement("div");
        spinner.id = "chart-spinner";
        spinner.className = "spinner";
        canvas.parentElement.appendChild(spinner);
    }
    spinner.style.display = "block";
}

function hideChartLoading() {
    const spinner = document.getElementById("chart-spinner");
    if (spinner) spinner.style.display = "none";
}

function showGoalsLoading() {
    const container = document.getElementById("goals-container");
    container.innerHTML = `
        <div class="skeleton-card">
            <div class="skeleton skeleton-text" style="width: 50%; height: 1.2rem;"></div>
            <div class="skeleton skeleton-text" style="height: 1rem;"></div>
        </div>
        <div class="skeleton-card">
            <div class="skeleton skeleton-text" style="width: 40%; height: 1.2rem;"></div>
            <div class="skeleton skeleton-text" style="height: 1rem;"></div>
        </div>
    `;
}

// Helpers para tratamento de erros amigáveis na UI

function showChartError(title, message) {
    hideChartLoading();
    document.getElementById("chartCategorias").style.display = "none";
    document.getElementById("chart-empty-state").style.display = "none";
    
    let errorPane = document.getElementById("chart-error-state");
    if (!errorPane) {
        errorPane = document.createElement("div");
        errorPane.id = "chart-error-state";
        errorPane.className = "error-pane";
        errorPane.style.position = "absolute";
        document.getElementById("chartCategorias").parentElement.appendChild(errorPane);
    }
    errorPane.innerHTML = `
        <i class="fa-solid fa-triangle-exclamation"></i>
        <h4>${title}</h4>
        <p>${message}</p>
        <button class="btn btn-mini btn-secondary" onclick="loadDashboardData()" style="padding: 0.4rem 1rem;">
            <i class="fa-solid fa-rotate-right"></i> Tentar Novamente
        </button>
    `;
    errorPane.style.display = "flex";
}

function hideChartError() {
    const errorPane = document.getElementById("chart-error-state");
    if (errorPane) errorPane.style.display = "none";
}

function showTableError(title, message) {
    const table = document.querySelector(".transactions-table-wrapper table");
    if (table) table.style.display = "none";
    document.getElementById("table-empty-state").style.display = "none";
    
    let errorPane = document.getElementById("table-error-state");
    if (!errorPane) {
        errorPane = document.createElement("div");
        errorPane.id = "table-error-state";
        errorPane.className = "error-pane";
        document.querySelector(".transactions-table-wrapper").appendChild(errorPane);
    }
    errorPane.innerHTML = `
        <i class="fa-solid fa-triangle-exclamation"></i>
        <h4>${title}</h4>
        <p>${message}</p>
        <button class="btn btn-mini btn-secondary" onclick="loadDashboardData()" style="padding: 0.4rem 1rem; width: auto; margin-top: 0.5rem;">
            <i class="fa-solid fa-rotate-right"></i> Recarregar Tabela
        </button>
    `;
    errorPane.style.display = "flex";
}

function hideTableError() {
    const table = document.querySelector(".transactions-table-wrapper table");
    if (table) table.style.display = "table";
    
    const errorPane = document.getElementById("table-error-state");
    if (errorPane) errorPane.style.display = "none";
}

function showGoalsError(title, message) {
    const container = document.getElementById("goals-container");
    container.innerHTML = `
        <div class="error-pane" style="margin: 0;">
            <i class="fa-solid fa-triangle-exclamation"></i>
            <h4>${title}</h4>
            <p>${message}</p>
            <button class="btn btn-mini btn-secondary" onclick="loadGoals()" style="padding: 0.4rem 1rem; width: auto; margin-top: 0.5rem;">
                <i class="fa-solid fa-rotate-right"></i> Tentar Novamente
            </button>
        </div>
    `;
}
