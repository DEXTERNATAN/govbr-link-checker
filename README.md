# 🔗 Crawler de Links do GOV.BR Design System

Este projeto é um crawler automatizado que extrai todos os links visíveis da página [https://www.gov.br/ds/home](https://www.gov.br/ds/home), renderizada via JavaScript, utilizando o Playwright. O objetivo é facilitar auditorias de conteúdo e verificação de integridade dos links relacionados ao Design System do governo brasileiro.

---

## 🚀 Funcionalidades

- ✅ Renderização de páginas com JavaScript usando o Playwright
- ✅ Extração de todos os links `<a href="">` presentes no DOM final
- ✅ Conversão de URLs relativas em absolutas
- ✅ Exportação para arquivo `links_extraidos.json`
- ✅ Automatização com Makefile ou script `setup.sh`

---

## ⚙️ Requisitos

- Python 3.9+
- [pip](https://pip.pypa.io/)
- [Playwright](https://playwright.dev/python/)

---

## 🛠️ Instalação

### 📦 Usando Makefile (recomendado)

```bash
make install
make run
```

### 🔧 Manualmente via `setup.sh`

```bash
chmod +x setup.sh
./setup.sh
```

---

## 🗂️ Estrutura

```
.
├── robots-crawler-links.py     # Script principal do crawler
├── links_extraidos.json        # Arquivo gerado com os links extraídos
├── requirements.txt            # Dependências Python
├── .gitignore                  # Arquivos ignorados no versionamento
├── Makefile                    # Automação de tarefas
├── setup.sh                    # Script de instalação alternativa
└── README.md                   # Este arquivo
```

---

## 📤 Saída esperada

Ao final da execução, será gerado um arquivo:

```bash
links_extraidos.json
```

Com todos os links encontrados em formato JSON.

---

## 👨‍💻 Autor

**Natanael Leite**  
Analista de Sistemas Sênior | Desenvolvedor de Software  
🚀 Projeto técnico para inspeção automatizada do site oficial do GOV.BR Design System

---

## 📄 Licença

Este projeto é livre para uso, sem fins lucrativos, e pode ser adaptado conforme as diretrizes da administração pública e normas técnicas de acessibilidade e transparência.
