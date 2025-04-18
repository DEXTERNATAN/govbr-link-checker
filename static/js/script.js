// Função para atualizar o estado dos botões de filtro
function updateFilterButtons(activeFilter) {
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    const isPressed = btn.textContent.toLowerCase().includes(activeFilter);
    btn.setAttribute("aria-pressed", isPressed);
  });
}

// Função para filtrar os resultados
function filtrar(tipo) {
  updateFilterButtons(tipo);
  const rows = document.querySelectorAll("tbody tr");
  let visibleRows = 0;

  rows.forEach((row) => {
    const status = row.querySelector(".status").textContent.toLowerCase();
    const shouldShow = tipo === "todos" || status.includes(tipo);
    row.style.display = shouldShow ? "" : "none";
    row.setAttribute("aria-hidden", !shouldShow);
    if (shouldShow) visibleRows++;
  });

  // Anunciar resultados com mais contexto
  const liveRegion =
    document.getElementById("filter-announcement") || createLiveRegion();
  const message = `${visibleRows} ${
    visibleRows === 1 ? "resultado encontrado" : "resultados encontrados"
  } para o filtro ${tipo}. Use as setas para navegar.`;
  liveRegion.textContent = message;

  // Focar no primeiro resultado visível
  const firstVisibleRow = document.querySelector('tbody tr[style=""]');
  if (firstVisibleRow) {
    const firstCell = firstVisibleRow.querySelector("td");
    if (firstCell) {
      firstCell.setAttribute("tabindex", "0");
      firstCell.focus();
    }
  }
}

// Criar região live para anúncios de leitores de tela
function createLiveRegion() {
  const region = document.createElement("div");
  region.id = "filter-announcement";
  region.setAttribute("role", "status");
  region.setAttribute("aria-live", "polite");
  region.style.position = "absolute";
  region.style.width = "1px";
  region.style.height = "1px";
  region.style.padding = "0";
  region.style.margin = "-1px";
  region.style.overflow = "hidden";
  region.style.clip = "rect(0, 0, 0, 0)";
  region.style.whiteSpace = "nowrap";
  region.style.border = "0";
  document.body.appendChild(region);
  return region;
}

// Suporte a navegação por teclado na tabela
document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector("table");
  if (!table) return;

  // Adicionar role e aria-sort para cabeçalhos ordenáveis
  table.querySelectorAll("th").forEach((th) => {
    if (th.onclick) {
      th.setAttribute("role", "columnheader");
      th.setAttribute("aria-sort", "none");
      th.setAttribute("tabindex", "0");
    }
  });

  // Adicionar eventos de teclado para ordenação
  table.addEventListener("keydown", (e) => {
    const target = e.target;
    if (target.tagName === "TH" && target.onclick) {
      if (e.key === "Enter" || e.key === " ") {
        e.preventDefault();
        target.click();

        // Atualizar aria-sort
        const isAscending = target.classList.contains("asc");
        target.setAttribute(
          "aria-sort",
          isAscending ? "ascending" : "descending"
        );
      }
    }
  });

  // Adicionar região com instruções de atalhos
  const instructions = document.createElement("div");
  instructions.setAttribute("role", "complementary");
  instructions.setAttribute("aria-label", "Atalhos de teclado");
  instructions.style.position = "absolute";
  instructions.style.left = "-9999px";
  instructions.innerHTML = `
    Atalhos disponíveis:
    Alt + 1: Mostrar todos os resultados
    Alt + 2: Filtrar status OK
    Alt + 3: Filtrar status Erro
    Alt + 4: Filtrar status Pendente
    Alt + E: Exportar para CSV
    Use Tab para navegar entre elementos e Enter para ativar
  `;
  document.body.appendChild(instructions);
});

// Gerenciamento de teclas de atalho
document.addEventListener("keydown", (e) => {
  // Alt + 1-4 para filtros rápidos
  if (e.altKey && ["1", "2", "3", "4"].includes(e.key)) {
    e.preventDefault();
    const filterMap = {
      1: "todos",
      2: "ok",
      3: "erro",
      4: "pendente",
    };
    filtrar(filterMap[e.key]);

    // Anunciar atalho usado
    const liveRegion =
      document.getElementById("filter-announcement") || createLiveRegion();
    liveRegion.textContent = `Filtro rápido ativado: ${filterMap[e.key]}`;
  }

  // Alt + E para exportar
  if (e.altKey && e.key.toLowerCase() === "e") {
    e.preventDefault();
    exportToCSV();
  }
});

// Função para exportar para CSV com feedback para leitores de tela
function exportToCSV() {
  try {
    // ... existing export code ...

    const liveRegion =
      document.getElementById("filter-announcement") || createLiveRegion();
    const visibleRows = document.querySelectorAll('tbody tr[style=""]').length;
    liveRegion.textContent = `Relatório exportado com sucesso. ${visibleRows} linhas exportadas para CSV.`;

    // Adicionar notificação visual
    const notification = document.createElement("div");
    notification.role = "alert";
    notification.className = "export-notification";
    notification.textContent = "Exportação concluída com sucesso!";
    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 3000);
  } catch (error) {
    const liveRegion =
      document.getElementById("filter-announcement") || createLiveRegion();
    liveRegion.textContent =
      "Erro ao exportar o relatório. Por favor, tente novamente.";
  }
}

// ... existing code ...
