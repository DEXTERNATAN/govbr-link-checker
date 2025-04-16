import json
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

# Definição dos caminhos dos arquivos
ARQUIVO_ENTRADA = "verificacao_links_quebrados.json"
ARQUIVO_SAIDA = "relatorio_links.html"

# Carrega os dados do arquivo JSON
with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
    dados = json.load(f)

# Obtém a data e hora atuais para inserir no relatório
now = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

# Processa os códigos HTTP para criar os dados do gráfico
http_codes = {}
for pai, info in dados.items():
    for link in info.get("links_pai", []):
        http = link.get("http_status")
        http_codes[str(http)] = http_codes.get(str(http), 0) + 1
    for filho in info.get("filhos", []):
        for subfilho in filho.get("subfilhos", []):
            http = subfilho.get("http_status")
            http_codes[str(http)] = http_codes.get(str(http), 0) + 1

# Configuração do Jinja2 para carregar os templates a partir da pasta 'templates'
env = Environment(loader=FileSystemLoader('templates'))
template = env.get_template('relatorio_template.html')

# Renderiza o template, passando os dados, a data/hora e os códigos HTTP
html = template.render(dados=dados, now=now, http_codes=http_codes)

# Salva o relatório gerado em um arquivo HTML
with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Relatório final gerado com sucesso em '{ARQUIVO_SAIDA}'")
