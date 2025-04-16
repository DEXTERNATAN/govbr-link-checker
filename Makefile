.PHONY: install run extrair mapear verificar relatorio clean

VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip

install:
	@echo "Criando ambiente virtual..."
	python3 -m venv $(VENV_DIR)
	@echo "Atualizando pip..."
	$(PIP) install --upgrade pip
	@echo "Instalando dependências..."
	$(PIP) install -r requirements.txt
	@echo "Instalando Playwright..."
	$(PYTHON) -m playwright install
	@echo "Instalação concluída."

run:
	@echo "Executando robots-crawler-links.py..."
	$(PYTHON) robots-crawler-links.py

extrair:
	@echo "Executando robots-crawler-links.py para extração..."
	$(PYTHON) robots-crawler-links.py

mapear:
	@echo "Executando mapear_links_secundarios.py..."
	$(PYTHON) mapear_links_secundarios.py

verificar:
	@echo "Executando verificar_links_quebrados.py..."
	$(PYTHON) verificar_links_quebrados.py

relatorio:
	@echo "Gerando relatório HTML com gerar_relatorio_html.py..."
	$(PYTHON) gerar_relatorio_html.py

clean:
	@echo "Removendo arquivos gerados..."
	rm -f links_extraidos.json links_apenas_filhos.json novos_links_por_pagina.json verificacao_links_quebrados.json relatorio_links.html
	@echo "Limpeza concluída."
