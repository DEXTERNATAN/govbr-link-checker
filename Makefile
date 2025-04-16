VENV_DIR=.venv
PYTHON=$(VENV_DIR)/bin/python
PIP=$(VENV_DIR)/bin/pip

install:
	python3 -m venv $(VENV_DIR)
	$(PIP) install -r requirements.txt
	$(PYTHON) -m playwright install

run:
	$(PYTHON) robots-crawler-links.py

extrair:
	$(PYTHON) robots-crawler-links.py

mapear:
	$(PYTHON) mapear_links_secundarios.py

verificar:
	$(PYTHON) verificar_links_quebrados.py

relatorio:
	$(PYTHON) gerar_relatorio_html.py

clean:
	rm -f links_extraidos.json links_apenas_filhos.json novos_links_por_pagina.json verificacao_links_quebrados.json relatorio_links.html
