// Variável global para armazenar o filtro atual
let filtroAtual = "todos";

// Função para atualizar o estado dos botões de filtro
function updateFilterButtons(activeFilter) {
  document.querySelectorAll(".filter-btn").forEach((btn) => {
    // Normaliza o texto do botão e o filtro ativo para comparação
    const buttonText = btn.textContent.trim().toLowerCase();
    const filterText = activeFilter.toLowerCase();

    // Verifica se o botão corresponde ao filtro ativo
    const isPressed =
      buttonText.includes(filterText) ||
      (filterText === "todos" && buttonText.includes("mostrar todos"));

    // Atualiza os atributos ARIA
    btn.setAttribute("aria-pressed", isPressed);

    // Atualiza as classes CSS
    if (isPressed) {
      btn.classList.add("filter-active");
    } else {
      btn.classList.remove("filter-active");
    }
  });
}

// Função para filtrar os resultados
function filtrar(tipo) {
  // Atualiza o filtro atual
  filtroAtual = tipo;

  // Atualiza os botões antes de filtrar
  updateFilterButtons(tipo);

  // Referências para todas as linhas nas tabelas
  const todasLinhas = document.querySelectorAll(".row-link");
  let visibleRows = 0;

  // Se o filtro for 'todos', simplesmente mostra tudo
  if (tipo === "todos") {
    todasLinhas.forEach((row) => {
      row.style.display = "";
      row.setAttribute("aria-hidden", "false");
      visibleRows++;
    });

    // Mostra todos os blocos de relatório
    document.querySelectorAll(".report-block").forEach((block) => {
      block.style.display = "";
    });

    // Mostra todas as subseções (filhos)
    document.querySelectorAll(".subsection").forEach((subsection) => {
      subsection.style.display = "";
    });
  } else {
    // Filtra linhas por status
    todasLinhas.forEach((row) => {
      const status = row.querySelector(".status").textContent.toLowerCase();
      const shouldShow = status.includes(tipo);
      row.style.display = shouldShow ? "" : "none";
      row.setAttribute("aria-hidden", !shouldShow);
      if (shouldShow) visibleRows++;
    });

    // Filtrar blocos pai (ocultar os que não têm nenhum resultado)
    document.querySelectorAll(".report-block").forEach((block) => {
      // Verifica se há alguma linha visível dentro deste bloco
      const temLinhasVisiveis = Array.from(
        block.querySelectorAll(".row-link")
      ).some((row) => row.style.display !== "none");
      block.style.display = temLinhasVisiveis ? "" : "none";
    });

    // Filtrar subseções de filhos (ocultar os que não têm nenhum resultado)
    document.querySelectorAll(".subsection").forEach((subsection) => {
      // Verifica se há alguma linha visível dentro desta subseção
      const temLinhasVisiveis = Array.from(
        subsection.querySelectorAll(".row-link")
      ).some((row) => row.style.display !== "none");
      subsection.style.display = temLinhasVisiveis ? "" : "none";
    });
  }

  // Anunciar resultados com mais contexto
  const liveRegion =
    document.getElementById("filter-announcement") || createLiveRegion();
  const message = `${visibleRows} ${
    visibleRows === 1 ? "resultado encontrado" : "resultados encontrados"
  } para o filtro ${tipo}. Use as setas para navegar.`;
  liveRegion.textContent = message;

  // Atualiza o texto do filtro ativo com o texto exato do botão
  const filtroAtivo = document.getElementById("filtro-ativo");
  const botaoAtivo = document.querySelector(`.filter-btn[aria-pressed="true"]`);
  if (filtroAtivo && botaoAtivo) {
    filtroAtivo.innerText = `Filtro atual: ${botaoAtivo.textContent.trim()}`;
  }

  // Focar no primeiro resultado visível
  const firstVisibleRow = document.querySelector('tbody tr[style=""]');
  if (firstVisibleRow) {
    const firstCell = firstVisibleRow.querySelector("td");
    if (firstCell) {
      firstCell.setAttribute("tabindex", "0");
      firstCell.focus();
    }
  }

  // Se não houver resultados, mostrar mensagem
  if (visibleRows === 0) {
    const mensagemVazia =
      document.getElementById("mensagem-vazia") || criarMensagemVazia();
    mensagemVazia.textContent = `Nenhum resultado encontrado para o filtro "${tipo}".`;
    mensagemVazia.style.display = "block";
  } else {
    const mensagemVazia = document.getElementById("mensagem-vazia");
    if (mensagemVazia) {
      mensagemVazia.style.display = "none";
    }
  }
}

// Função para criar mensagem de resultados vazios
function criarMensagemVazia() {
  const mensagem = document.createElement("div");
  mensagem.id = "mensagem-vazia";
  mensagem.className = "mensagem-vazia";
  mensagem.setAttribute("role", "alert");
  mensagem.style.textAlign = "center";
  mensagem.style.padding = "30px";
  mensagem.style.marginTop = "20px";
  mensagem.style.backgroundColor = "var(--background-medium)";
  mensagem.style.borderRadius = "8px";
  mensagem.style.color = "var(--text-medium)";
  mensagem.style.fontWeight = "bold";

  const reportSections = document.querySelector(".report-sections");
  reportSections.appendChild(mensagem);

  return mensagem;
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

  // Aplicar o filtro inicial 'todos'
  filtrar("todos");

  // Adicionar estilos CSS para o botão ativo
  const style = document.createElement("style");
  style.textContent = `
    .filter-btn.filter-active {
      background: var(--accent-dark) !important;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2) inset;
      transform: translateY(1px);
    }
  `;
  document.head.appendChild(style);

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
