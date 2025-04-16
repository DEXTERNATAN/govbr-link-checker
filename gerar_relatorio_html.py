 
# import json

# ARQUIVO_ENTRADA = "verificacao_links_quebrados.json"
# ARQUIVO_SAIDA = "relatorio_links.html"

# with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
#     dados = json.load(f)

# http_codes = {}
# html = """
# <!DOCTYPE html>
# <html lang="pt-br">
# <head>
#     <meta charset="UTF-8">
#     <title>Relatório de Verificação de Links</title>
#     <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
#     <style>
#         body {
#             font-family: Arial, sans-serif;
#             margin: 2rem;
#             background: #f4f4f4;
#         }
#         h1, h2, h3 {
#             color: #333;
#         }
#         .section {
#             margin-bottom: 2rem;
#             background: #fff;
#             padding: 1rem;
#             border-radius: 8px;
#             box-shadow: 0 0 10px rgba(0,0,0,0.05);
#         }
#         table {
#             width: 100%;
#             border-collapse: collapse;
#             margin-top: 1rem;
#         }
#         th, td {
#             border: 1px solid #ccc;
#             padding: 8px;
#             font-size: 14px;
#         }
#         th {
#             background: #007bff;
#             color: #fff;
#             text-align: left;
#         }
#         tr:nth-child(even) {
#             background: #f9f9f9;
#         }
#         .ok { color: green; font-weight: bold; }
#         .erro { color: red; font-weight: bold; }
#         .export-btn, .filter-btn {
#             padding: 6px 12px;
#             border: none;
#             border-radius: 4px;
#             margin: 5px 5px 15px 0;
#             font-weight: bold;
#             cursor: pointer;
#         }
#         .export-btn {
#             background: #28a745;
#             color: white;
#         }
#         .filter-btn {
#             background: #ffc107;
#             color: #000;
#         }
#     </style>
# </head>
# <body>
#     <h1>Relatório de Verificação de Links</h1>

#     <div class="section">
#         <h2>📈 Resumo Estatístico</h2>
#         <p><strong>Total de links:</strong> <span id="total_links">0</span></p>
#         <p>
#             <strong>OK:</strong> <span id="ok_count">0</span> |
#             <strong>HTTP Error:</strong> <span id="http_error_count">0</span> |
#             <strong>Inexistente:</strong> <span id="inexistente_count">0</span> |
#             <strong>Erro de carregamento:</strong> <span id="carregamento_count">0</span> |
#             <strong>Sem resposta:</strong> <span id="sem_resposta_count">0</span>
#         </p>
#         <h3>Filtros</h3>
#         <button onclick="filtrar('todos')" class="filter-btn">Mostrar Todos</button>
#         <button onclick="filtrar('ok')" class="filter-btn">Somente OK</button>
#         <button onclick="filtrar('http')" class="filter-btn">Somente HTTP Error</button>
#         <button onclick="filtrar('inexistente')" class="filter-btn">Somente Inexistente</button>
#         <button onclick="filtrar('carregamento')" class="filter-btn">Somente Erro de Carregamento</button>
#         <button onclick="filtrar('sem resposta')" class="filter-btn">Somente Sem Resposta</button>
#         <button onclick="exportToCSV()" class="export-btn">📁 Exportar CSV</button>
#     </div>

#     <canvas id="httpChart" height="100"></canvas>
#     <textarea id="csv_data" style="display:none;">pai,filho,subfilho,status,http_status\n</textarea>
# """

# for pai, info in dados.items():
#     html += f"""
#     <div class="section">
#         <h2>🧩 Seção Pai: {pai}</h2>
#         <p><strong>URL Pai:</strong> <a href="{info['url_pai']}" target="_blank">{info['url_pai']}</a></p>
#         <p><strong>Tempo:</strong> {info.get('tempo_pai', 0)}s</p>
#     """

#     erro_pai = info.get("erro_pai", {})
#     if erro_pai.get("ocorreu"):
#         html += f"""<p><strong>Erro Pai:</strong> {json.dumps(erro_pai, ensure_ascii=False)}</p>"""

#     html += """
#         <h3>🔗 Links do Pai</h3>
#         <table>
#             <tr>
#                 <th>URL</th>
#                 <th>Status</th>
#                 <th>HTTP</th>
#             </tr>
#     """

#     for link_info in info.get("links_pai", []):
#         url = link_info["url"]
#         status = link_info["status"]
#         http = link_info.get("http_status")
#         status_class = "ok" if status == "ok" else "erro"
#         http_text = http if http is not None else "-"
#         http_codes[str(http)] = http_codes.get(str(http), 0) + 1
#         html += f"""
#             <tr class="row-link">
#                 <td><a href="{url}" target="_blank">{url}</a></td>
#                 <td class="{status_class}">{status}</td>
#                 <td>{http_text}</td>
#             </tr>
#         """
#         html += f'<script>document.getElementById("csv_data").value += `{pai},PAI,{url},{status},{http_text}\\n`;</script>'

#     html += "</table>"

#     for filho in info.get("filhos", []):
#         html += f"""
#         <h3>📄 Filho: <a href="{filho['url']}" target="_blank">{filho['url']}</a></h3>
#         <p><strong>Tempo:</strong> {filho.get("tempo", 0)}s</p>
#         """

#         erro_filho = filho.get("erro", {})
#         if erro_filho.get("ocorreu"):
#             html += f"""<p><strong>Erro:</strong> {json.dumps(erro_filho, ensure_ascii=False)}</p>"""

#         html += """
#         <table>
#             <tr>
#                 <th>URL Subfilho</th>
#                 <th>Status</th>
#                 <th>HTTP</th>
#             </tr>
#         """
#         for subfilho in filho.get("subfilhos", []):
#             url = subfilho["url"]
#             status = subfilho["status"]
#             http = subfilho.get("http_status")
#             status_class = "ok" if status == "ok" else "erro"
#             http_text = http if http is not None else "-"
#             http_codes[str(http)] = http_codes.get(str(http), 0) + 1
#             html += f"""
#             <tr class="row-link">
#                 <td><a href="{url}" target="_blank">{url}</a></td>
#                 <td class="{status_class}">{status}</td>
#                 <td>{http_text}</td>
#             </tr>
#             """
#             html += f'<script>document.getElementById("csv_data").value += `{pai},{filho["url"]},{url},{status},{http_text}\\n`;</script>'

#         html += "</table>"

#     html += "</div>"

# labels = list(http_codes.keys())
# counts = list(http_codes.values())

# html += f"""
# <script>
#     const ctx = document.getElementById('httpChart').getContext('2d');
#     new Chart(ctx, {{
#         type: 'bar',
#         data: {{
#             labels: {labels},
#             datasets: [{{
#                 label: 'Ocorrências por HTTP Status',
#                 data: {counts},
#                 backgroundColor: 'rgba(0,123,255,0.6)',
#                 borderColor: 'rgba(0,123,255,1)',
#                 borderWidth: 1
#             }}]
#         }},
#         options: {{
#             scales: {{
#                 y: {{ beginAtZero: true }},
#                 x: {{ title: {{ display: true, text: 'HTTP Status Code' }} }}
#             }}
#         }}
#     }});

#     const todasLinhas = Array.from(document.querySelectorAll(".row-link"));
#     let total = 0, ok = 0, httpError = 0, inexistente = 0, carregamento = 0, semResposta = 0;

#     todasLinhas.forEach(row => {{
#         const status = row.children[1].innerText.toLowerCase();
#         total++;
#         if (status === "ok") ok++;
#         else if (status.includes("http")) httpError++;
#         else if (status.includes("inexistente")) inexistente++;
#         else if (status.includes("carregamento")) carregamento++;
#         else if (status.includes("sem resposta")) semResposta++;
#     }});

#     document.getElementById("total_links").innerText = total;
#     document.getElementById("ok_count").innerText = ok;
#     document.getElementById("http_error_count").innerText = httpError;
#     document.getElementById("inexistente_count").innerText = inexistente;
#     document.getElementById("carregamento_count").innerText = carregamento;
#     document.getElementById("sem_resposta_count").innerText = semResposta;

#     function filtrar(tipo) {{
#         todasLinhas.forEach(row => {{
#             const status = row.children[1].innerText.toLowerCase();
#             row.style.display = "table-row";
#             if (tipo === "todos") return;
#             if (tipo === "ok" && status !== "ok") row.style.display = "none";
#             if (tipo === "http" && !status.includes("http")) row.style.display = "none";
#             if (tipo === "inexistente" && !status.includes("inexistente")) row.style.display = "none";
#             if (tipo === "carregamento" && !status.includes("carregamento")) row.style.display = "none";
#             if (tipo === "sem resposta" && !status.includes("sem resposta")) row.style.display = "none";
#         }});
#     }}

#     function exportToCSV() {{
#         const data = document.getElementById('csv_data').value;
#         const blob = new Blob([data], {{ type: 'text/csv;charset=utf-8;' }});
#         const url = URL.createObjectURL(blob);
#         const a = document.createElement('a');
#         a.href = url;
#         a.download = 'relatorio_links.csv';
#         a.click();
#     }}
# </script>
# </body>
# </html>
# """

# with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
#     f.write(html)

# print(f"✅ Relatório final gerado com sucesso em '{ARQUIVO_SAIDA}'")

 
import json

ARQUIVO_ENTRADA = "verificacao_links_quebrados.json"
ARQUIVO_SAIDA = "relatorio_links.html"

with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
    dados = json.load(f)

http_codes = {}
html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Verificação de Links</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
                 body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 2rem;
            background: #f0f2f5;
            color: #444;
        }
        .section {
            margin-bottom: 2rem;
            background: #fff;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        table {
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            overflow: hidden;
            border-radius: 8px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }
        th, td {
            padding: 12px 15px;
            text-align: left;
        }
        th {
            background-color: #4a90e2;
            color: white;
            font-weight: 600;
        }
        td {
            border-bottom: 1px solid #ddd;
        }
        tr:hover td {
            background-color: #f1faff;
        }
        tr:nth-child(even) td {
            background-color: #fafafa;
        }
        .ok { color: #27ae60; font-weight: 600; }
        .erro { color: #e74c3c; font-weight: 600; }
        a { color: #3498db; text-decoration: none; }
        a:hover { text-decoration: underline; }
        .export-btn, .filter-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin-right: 10px;
            transition: background 0.3s;
        }
        .export-btn { background: #2ecc71; color: #fff; }
        .filter-btn { background: #f39c12; color: #fff; }
        .export-btn:hover { background: #27ae60; }
        .filter-btn:hover { background: #e67e22; }
    </style>
</head>
<body>
    <h1>Relatório de Verificação de Links</h1>

    
"""

for pai, info in dados.items():
    html += f"""
    <div class="section">
        <h2>🧩 Seção Pai: {pai}</h2>
        <p><strong>URL Pai:</strong> <a href="{info['url_pai']}" target="_blank">{info['url_pai']}</a></p>
        <p><strong>Tempo:</strong> {info.get('tempo_pai', 0)}s</p>
    """

    erro_pai = info.get("erro_pai", {})
    if erro_pai.get("ocorreu"):
        html += f"""<p><strong>Erro Pai:</strong> {json.dumps(erro_pai, ensure_ascii=False)}</p>"""

    html += """
        <h3>🔗 Links do Pai</h3>
        <table>
            <tr>
                <th>URL</th>
                <th>Status</th>
                <th>HTTP</th>
            </tr>
    """

    for link_info in info.get("links_pai", []):
        url = link_info["url"]
        status = link_info["status"]
        http = link_info.get("http_status")
        status_class = "ok" if status == "ok" else "erro"
        http_text = http if http is not None else "-"
        http_codes[str(http)] = http_codes.get(str(http), 0) + 1
        html += f"""
            <tr class="row-link">
                <td><a href="{url}" target="_blank">{url}</a></td>
                <td class="{status_class}">{status}</td>
                <td>{http_text}</td>
            </tr>
        """
        html += f'<script>document.getElementById("csv_data").value += `{pai},PAI,{url},{status},{http_text}\\n`;</script>'

    html += "</table>"

    for filho in info.get("filhos", []):
        html += f"""
        <h3>📄 Filho: <a href="{filho['url']}" target="_blank">{filho['url']}</a></h3>
        <p><strong>Tempo:</strong> {filho.get("tempo", 0)}s</p>
        """

        erro_filho = filho.get("erro", {})
        if erro_filho.get("ocorreu"):
            html += f"""<p><strong>Erro:</strong> {json.dumps(erro_filho, ensure_ascii=False)}</p>"""

        html += """
        <table>
            <tr>
                <th>URL Subfilho</th>
                <th>Status</th>
                <th>HTTP</th>
            </tr>
        """
        for subfilho in filho.get("subfilhos", []):
            url = subfilho["url"]
            status = subfilho["status"]
            http = subfilho.get("http_status")
            status_class = "ok" if status == "ok" else "erro"
            http_text = http if http is not None else "-"
            http_codes[str(http)] = http_codes.get(str(http), 0) + 1
            html += f"""
            <tr class="row-link">
                <td><a href="{url}" target="_blank">{url}</a></td>
                <td class="{status_class}">{status}</td>
                <td>{http_text}</td>
            </tr>
            """
            html += f'<script>document.getElementById("csv_data").value += `{pai},{filho["url"]},{url},{status},{http_text}\\n`;</script>'

        html += "</table>"

    html += "</div>"

labels = list(http_codes.keys())
counts = list(http_codes.values())

html += f"""
<script>
    const ctx = document.getElementById('httpChart').getContext('2d');
    new Chart(ctx, {{
        type: 'bar',
        data: {{
            labels: {labels},
            datasets: [{{
                label: 'Ocorrências por HTTP Status',
                data: {counts},
                backgroundColor: 'rgba(0,123,255,0.6)',
                borderColor: 'rgba(0,123,255,1)',
                borderWidth: 1
            }}]
        }},
        options: {{
            scales: {{
                y: {{ beginAtZero: true }},
                x: {{ title: {{ display: true, text: 'HTTP Status Code' }} }}
            }}
        }}
    }});

    const todasLinhas = Array.from(document.querySelectorAll(".row-link"));
    let total = 0, ok = 0, httpError = 0, inexistente = 0, carregamento = 0, semResposta = 0;

    todasLinhas.forEach(row => {{
        const status = row.children[1].innerText.toLowerCase();
        total++;
        if (status === "ok") ok++;
        else if (status.includes("http")) httpError++;
        else if (status.includes("inexistente")) inexistente++;
        else if (status.includes("carregamento")) carregamento++;
        else if (status.includes("sem resposta")) semResposta++;
    }});

    document.getElementById("total_links").innerText = total;
    document.getElementById("ok_count").innerText = ok;
    document.getElementById("http_error_count").innerText = httpError;
    document.getElementById("inexistente_count").innerText = inexistente;
    document.getElementById("carregamento_count").innerText = carregamento;
    document.getElementById("sem_resposta_count").innerText = semResposta;

    function filtrar(tipo) {{
        todasLinhas.forEach(row => {{
            const status = row.children[1].innerText.toLowerCase();
            row.style.display = "table-row";
            if (tipo === "todos") return;
            if (tipo === "ok" && status !== "ok") row.style.display = "none";
            if (tipo === "http" && !status.includes("http")) row.style.display = "none";
            if (tipo === "inexistente" && !status.includes("inexistente")) row.style.display = "none";
            if (tipo === "carregamento" && !status.includes("carregamento")) row.style.display = "none";
            if (tipo === "sem resposta" && !status.includes("sem resposta")) row.style.display = "none";
        }});
    }}

    function exportToCSV() {{
        const data = document.getElementById('csv_data').value;
        const blob = new Blob([data], {{ type: 'text/csv;charset=utf-8;' }});
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'relatorio_links.csv';
        a.click();
    }}
</script>
</body>
</html>
"""

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Relatório final gerado com sucesso em '{ARQUIVO_SAIDA}'")