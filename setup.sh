#!/bin/bash

echo "🔧 Criando virtualenv..."
python3 -m venv .venv

echo "📦 Instalando dependências do requirements.txt..."
./.venv/bin/pip install -r requirements.txt

echo "🌐 Instalando navegadores do Playwright..."
./.venv/bin/python -m playwright install

echo "🚀 Executando o script..."
./.venv/bin/python robots-crawler-links.py
