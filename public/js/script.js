// Variável global para armazenar o filtro atual
let filtroAtual = "todos";

// Função para inicializar o gráfico
function inicializarGrafico() {
  const ctx = document.getElementById("httpChart")?.getContext("2d");
  if (!ctx) return;

  // Função para ajustar o tamanho da fonte baseado na largura da tela
  function getFontSize() {
    return window.innerWidth < 480 ? 10 : window.innerWidth < 768 ? 12 : 14;
  }

  // Os dados do gráfico são gerados pelo backend
  const chart = new Chart(ctx, {
    type: "bar",
    data: window.httpCodesData || {
      labels: [],
      datasets: [
        {
          label: "Ocorrências por HTTP Status",
          data: [],
          backgroundColor: "rgba(54, 162, 235, 0.6)",
          borderColor: "rgba(54, 162, 235, 1)",
          borderWidth: 1,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          ticks: {
            font: {
              size: getFontSize(),
            },
          },
        },
        x: {
          title: {
            display: true,
            text: "Código HTTP",
            font: {
              size: getFontSize(),
            },
          },
          ticks: {
            font: {
              size: getFontSize(),
            },
          },
        },
      },
      plugins: {
        legend: {
          labels: {
            font: {
              size: getFontSize(),
            },
          },
        },
      },
    },
  });

  // Atualiza o tamanho da fonte quando a janela é redimensionada
  window.addEventListener("resize", function () {
    chart.options.scales.x.ticks.font.size = getFontSize();
    chart.options.scales.y.ticks.font.size = getFontSize();
    chart.options.plugins.legend.labels.font.size = getFontSize();
    chart.update();
  });
}

// Função para calcular estatísticas
function calcularEstatisticas() {
  const todasLinhas = Array.from(document.querySelectorAll(".row-link"));
  let total = 0,
    ok = 0,
    httpError = 0,
    inexistente = 0,
    carregamento = 0,
    semResposta = 0;

  todasLinhas.forEach((row) => {
    const status = row
      .querySelector("td:nth-child(2)")
      .textContent.toLowerCase();
    total++;
    if (status === "ok") ok++;
    else if (status.includes("http")) httpError++;
    else if (status.includes("inexistente")) inexistente++;
    else if (status.includes("carregamento")) carregamento++;
    else if (status.includes("sem resposta") || status.includes("timeout"))
      semResposta++;
  });

  document.getElementById("total_links").innerText = total;
  document.getElementById("ok_count").innerText = ok;
  document.getElementById("http_error_count").innerText = httpError;
  document.getElementById("inexistente_count").innerText = inexistente;
  document.getElementById("carregamento_count").innerText = carregamento;
  document.getElementById("sem_resposta_count").innerText = semResposta;
}

// Função para atualizar o estado dos botões de filtro
function updateFilterButtons(activeFilter) {
  document.querySelectorAll(".filter-btn, .error-only-btn").forEach((btn) => {
    // Para o botão de erro, tratamos de forma especial
    if (btn.classList.contains("error-only-btn")) {
      btn.setAttribute("aria-pressed", activeFilter === "apenas_erros");
      btn.classList.toggle("filter-active", activeFilter === "apenas_erros");
      return;
    }

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
      const status = row
        .querySelector("td:nth-child(2)")
        .textContent.toLowerCase();

      // Verifica se o status contém o texto do filtro
      let shouldShow = false;

      // Casos especiais de filtros
      if (tipo === "sem resposta") {
        // Inclui tanto "sem resposta" quanto "timeout"
        shouldShow =
          status.includes("sem resposta") || status.includes("timeout");
      } else if (tipo === "http") {
        // Inclui todos os erros HTTP (400-599)
        shouldShow =
          status.includes("http") &&
          (status.includes("erro") ||
            status.includes("não encontrado") ||
            status.includes("proibido") ||
            status.includes("não autorizado") ||
            status.includes("servidor"));
      } else if (tipo === "carregamento") {
        // Inclui erros de carregamento, conexão, SSL e outros
        shouldShow =
          status.includes("carregamento") ||
          status.includes("conexão") ||
          status.includes("ssl") ||
          status.includes("erro http2") ||
          status.includes("dns");
      } else if (tipo === "inexistente") {
        // Páginas inexistentes
        shouldShow = status.includes("inexistente");
      } else if (tipo === "ok") {
        // Somente status OK
        shouldShow = status === "ok";
      } else {
        // Fallback para qualquer outro tipo de filtro
        shouldShow = status.includes(tipo);
      }

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

      // Se este bloco pai estiver visível, marca-o visualmente como contendo erro
      if (temLinhasVisiveis && tipo !== "ok") {
        block.classList.add("contains-error");
      } else {
        block.classList.remove("contains-error");
      }
    });

    // Filtrar subseções de filhos (ocultar os que não têm nenhum resultado)
    document.querySelectorAll(".subsection").forEach((subsection) => {
      // Verifica se há alguma linha visível dentro desta subseção
      const temLinhasVisiveis = Array.from(
        subsection.querySelectorAll(".row-link")
      ).some((row) => row.style.display !== "none");
      subsection.style.display = temLinhasVisiveis ? "" : "none";

      // Se esta subseção estiver visível, marca-a visualmente como contendo erro
      if (temLinhasVisiveis && tipo !== "ok") {
        subsection.classList.add("contains-error");
      } else {
        subsection.classList.remove("contains-error");
      }
    });

    // Destaca visualmente as linhas que correspondem ao filtro
    todasLinhas.forEach((row) => {
      if (row.style.display !== "none") {
        row.classList.add("filtered-row");
      } else {
        row.classList.remove("filtered-row");
      }
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
  const botaoAtivo = document.querySelector(
    `.filter-btn[aria-pressed="true"], .error-only-btn[aria-pressed="true"]`
  );
  if (filtroAtivo && botaoAtivo) {
    filtroAtivo.innerText = `Filtro atual: ${botaoAtivo.textContent.trim()}`;
  }

  // Focar no primeiro resultado visível
  const firstVisibleRow = document.querySelector('.row-link[style=""]');
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

// Função para filtrar e mostrar apenas elementos com erro
function filtrarApenasErros() {
  // Atualiza o filtro atual
  filtroAtual = "apenas_erros";

  // Atualiza os botões para mostrar qual está ativo
  updateFilterButtons(filtroAtual);

  // Primeiro, mostra todas as linhas
  document.querySelectorAll(".row-link").forEach((row) => {
    row.style.display = "";
    row.setAttribute("aria-hidden", "false");
  });

  // Oculta elementos que não contêm erros
  document.querySelectorAll(".report-block").forEach((block) => {
    // Verifica se o bloco tem a indicação de erro_links_pai
    const statusElement = block.querySelector(".status-links-pai .erro");
    if (!statusElement) {
      block.style.display = "none";
    } else {
      // Adiciona classe de destaque visual
      block.classList.add("contains-error");
    }
  });

  // Atualiza o texto do filtro ativo
  const filtroAtivo = document.getElementById("filtro-ativo");
  if (filtroAtivo) {
    filtroAtivo.innerText = "Filtro atual: Mostrar Apenas Erros";
  }

  // Anunciar para leitores de tela
  const liveRegion =
    document.getElementById("filter-announcement") || createLiveRegion();
  const blocoVisiveis = document.querySelectorAll(
    '.report-block[style=""]'
  ).length;
  liveRegion.textContent = `Mostrando ${blocoVisiveis} seções com erro. Use as setas para navegar.`;
}

// Funções para o modal de URLs
function setupURLModals() {
  // Adicionar modal ao body se não existir
  if (!document.getElementById("urlModal")) {
    const modalHTML = `
      <div id="urlModal" class="url-modal" role="dialog" aria-labelledby="modalTitle" aria-modal="true">
        <div class="url-modal-content">
          <div class="url-modal-header">
            <h3 id="modalTitle">URL Completa</h3>
            <button class="url-modal-close" aria-label="Fechar modal">&times;</button>
          </div>
          <div class="url-modal-body">
            <div class="url-full" id="urlFull"></div>
            <div class="url-actions">
              <button class="url-modal-button" id="copyURLButton">Copiar URL</button>
              <button class="url-modal-button" id="visitURLButton">Visitar Link</button>
            </div>
            <div class="copy-success" id="copySuccess">URL copiada com sucesso!</div>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML("beforeend", modalHTML);

    // Configurar eventos do modal
    const modal = document.getElementById("urlModal");
    const closeBtn = modal.querySelector(".url-modal-close");
    const copyBtn = document.getElementById("copyURLButton");
    const visitBtn = document.getElementById("visitURLButton");
    const copySuccess = document.getElementById("copySuccess");

    closeBtn.addEventListener("click", closeURLModal);

    // Fechar modal ao clicar fora
    modal.addEventListener("click", (e) => {
      if (e.target === modal) {
        closeURLModal();
      }
    });

    // Botão de copiar URL
    copyBtn.addEventListener("click", () => {
      const urlText = document.getElementById("urlFull").textContent;
      navigator.clipboard
        .writeText(urlText)
        .then(() => {
          copySuccess.style.display = "block";
          setTimeout(() => {
            copySuccess.style.display = "none";
          }, 3000);
        })
        .catch((err) => {
          console.error("Erro ao copiar URL: ", err);
          alert(
            "Não foi possível copiar a URL automaticamente. Por favor, selecione o texto e copie manualmente."
          );
        });
    });

    // Botão de visitar link
    visitBtn.addEventListener("click", () => {
      const urlText = document.getElementById("urlFull").textContent;
      window.open(urlText, "_blank");
    });
  }

  // Adicionar ícones de cópia e eventos às células de URL
  const urlCells = document.querySelectorAll(".data-table td:first-child");
  urlCells.forEach((cell) => {
    const link = cell.querySelector("a");
    if (link && !cell.querySelector(".copy-icon")) {
      const fullURL = link.href;
      const copyIcon = document.createElement("span");
      copyIcon.className = "copy-icon";
      copyIcon.innerHTML = "📋";
      copyIcon.setAttribute("aria-label", "Ver URL completa e copiar");
      copyIcon.setAttribute("role", "button");
      copyIcon.setAttribute("tabindex", "0");

      copyIcon.addEventListener("click", () => {
        openURLModal(fullURL, link.textContent);
      });

      // Suporte para teclado
      copyIcon.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openURLModal(fullURL, link.textContent);
        }
      });

      cell.appendChild(copyIcon);
    }
  });
}

function openURLModal(url, displayText) {
  const modal = document.getElementById("urlModal");
  const urlFull = document.getElementById("urlFull");

  // Configurar conteúdo do modal
  urlFull.textContent = url;
  document.getElementById("modalTitle").textContent =
    "URL Completa: " +
    displayText.substring(0, 30) +
    (displayText.length > 30 ? "..." : "");

  // Exibir modal
  modal.style.display = "flex";

  // Adicionar trap focus para acessibilidade
  const focusableElements = modal.querySelectorAll("button");
  const firstFocusableElement = focusableElements[0];
  const lastFocusableElement = focusableElements[focusableElements.length - 1];

  // Focar no primeiro elemento
  firstFocusableElement.focus();

  // Adicionar event listener para trap focus
  modal.addEventListener("keydown", handleTabKey);

  function handleTabKey(e) {
    if (e.key === "Escape") {
      closeURLModal();
      return;
    }

    if (e.key !== "Tab") return;

    if (e.shiftKey) {
      if (document.activeElement === firstFocusableElement) {
        lastFocusableElement.focus();
        e.preventDefault();
      }
    } else {
      if (document.activeElement === lastFocusableElement) {
        firstFocusableElement.focus();
        e.preventDefault();
      }
    }
  }
}

function closeURLModal() {
  const modal = document.getElementById("urlModal");
  modal.style.display = "none";
  document.getElementById("copySuccess").style.display = "none";
}

// Suporte a navegação por teclado na tabela
document.addEventListener("DOMContentLoaded", () => {
  // Inicializar o gráfico
  inicializarGrafico();

  // Calcular estatísticas
  calcularEstatisticas();

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
    .filter-btn.filter-active, .error-only-btn.filter-active {
      background: var(--accent-dark) !important;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2) inset;
      transform: translateY(1px);
    }
    
    .error-only-btn {
      background: var(--error);
      color: var(--text-light);
      font-weight: 500;
    }
    
    .error-only-btn.filter-active {
      background: var(--error-dark) !important;
      box-shadow: 0 2px 4px rgba(0,0,0,0.2) inset;
    }
    
    .contains-error {
      border-left: 4px solid var(--error) !important;
      background-color: var(--error-light);
    }
    
    .filtered-row {
      background-color: var(--accent-light) !important;
      font-weight: bold;
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

  // Inicializar os modais de URL
  setupURLModals();
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

  // Alt + F para mostrar apenas erros
  if (e.altKey && e.key.toLowerCase() === "f") {
    e.preventDefault();
    filtrarApenasErros();
  }
});

// Função para exportar para CSV com feedback para leitores de tela
function exportToCSV() {
  try {
    const data = document.getElementById("csv_data").value;
    const blob = new Blob([data], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "relatorio_links.csv";
    a.click();

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
