import json

ARQUIVO_ENTRADA = "verificacao_links_quebrados.json"
ARQUIVO_SAIDA = "relatorio_links.html"

with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
    dados = json.load(f)

html = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>Relatório de Verificação de Links</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 2rem;
            background: #f5f5f5;
        }
        h1 {
            color: #333;
        }
        table {
            border-collapse: collapse;
            width: 100%;
            background: #fff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        th, td {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: left;
            font-size: 14px;
        }
        th {
            background: #007bff;
            color: white;
        }
        tr:nth-child(even) {
            background: #f9f9f9;
        }
        .erro {
            color: red;
            font-weight: bold;
        }
        .ok {
            color: green;
        }
    </style>
</head>
<body>
    <h1>Relatório de Verificação de Links</h1>
    <table>
        <thead>
            <tr>
                <th>Seção Pai</th>
                <th>URL Pai</th>
                <th>Link Filho</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody>
"""

for item in dados:
    status_class = "ok" if item["status"] == "ok" else "erro"
    html += f"""
        <tr>
            <td>{item['pai']}</td>
            <td><a href="{item['url_pai']}" target="_blank">{item['url_pai']}</a></td>
            <td><a href="{item['filho']}" target="_blank">{item['filho']}</a></td>
            <td class="{status_class}">{item['status']}</td>
        </tr>
    """

html += """
        </tbody>
    </table>
</body>
</html>
"""

with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Relatório HTML gerado com sucesso em '{ARQUIVO_SAIDA}'")
