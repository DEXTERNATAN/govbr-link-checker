import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Definição dos caminhos dos arquivos e diretórios
DIRETORIO_BASE = Path(__file__).parent
DIRETORIO_PUBLIC = DIRETORIO_BASE / "public"
ARQUIVO_ENTRADA = DIRETORIO_BASE / "verificacao_links_quebrados.json"
ARQUIVO_SAIDA = DIRETORIO_PUBLIC / "relatorio_links.html"

def criar_diretorio_se_nao_existe(diretorio):
    """Cria o diretório se ele não existir."""
    if not diretorio.exists():
        try:
            diretorio.mkdir(parents=True)
            print(f"✅ Diretório '{diretorio}' criado com sucesso.")
        except Exception as e:
            print(f"❌ Erro ao criar diretório '{diretorio}': {str(e)}")
            raise

def copiar_arquivos_estaticos():
    """Copia os arquivos estáticos necessários para a pasta public."""
    arquivos_estaticos = [
        ("static/js/script.js", "js/script.js"),
        ("styles.css", "styles.css")
    ]
    
    for origem, destino in arquivos_estaticos:
        origem_path = DIRETORIO_BASE / origem
        destino_path = DIRETORIO_PUBLIC / destino
        
        # Cria o diretório de destino se necessário
        destino_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            if origem_path.exists():
                with open(origem_path, "r", encoding="utf-8") as f_origem:
                    conteudo = f_origem.read()
                
                with open(destino_path, "w", encoding="utf-8") as f_destino:
                    f_destino.write(conteudo)
                print(f"✅ Arquivo '{origem}' copiado para '{destino}'")
            else:
                print(f"⚠️ Arquivo de origem '{origem}' não encontrado")
        except Exception as e:
            print(f"❌ Erro ao copiar arquivo '{origem}': {str(e)}")

def main():
    try:
        # Cria o diretório public se não existir
        criar_diretorio_se_nao_existe(DIRETORIO_PUBLIC)
        
        # Verifica se o arquivo de entrada existe
        if not ARQUIVO_ENTRADA.exists():
            raise FileNotFoundError(f"Arquivo de entrada '{ARQUIVO_ENTRADA}' não encontrado")
        
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

        # Configuração do Jinja2 para carregar os templates
        env = Environment(loader=FileSystemLoader('templates'))
        template = env.get_template('relatorio_template.html')

        # Renderiza o template
        html = template.render(dados=dados, now=now, http_codes=http_codes)

        # Salva o relatório gerado na pasta public
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"✅ Relatório gerado com sucesso em '{ARQUIVO_SAIDA}'")
        
        # Copia os arquivos estáticos necessários
        copiar_arquivos_estaticos()
        
        print("✅ Processo finalizado com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro durante a geração do relatório: {str(e)}")
        raise

if __name__ == "__main__":
    main()
