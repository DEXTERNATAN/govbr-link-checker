import asyncio
import json
from urllib.parse import urljoin
from playwright.async_api import async_playwright

ARQUIVO_ENTRADA = "links_apenas_filhos.json"
ARQUIVO_SAIDA = "novos_links_por_pagina.json"
BASE_URL = "https://www.gov.br/ds/"

async def mapear_novos_links():
    # Carrega os links filhos do arquivo anterior
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        estrutura = json.load(f)

    # Mapeia pai -> [urls dos filhos]
    urls_por_pai = {}
    for bloco in estrutura:
        for pai, conteudo in bloco.items():
            filhos = conteudo[0]["filhos"]
            urls_por_pai[pai] = [filho_info["url"] for filho_info in filhos.values()]

    resultado = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for pai, urls_filhos in urls_por_pai.items():
            url_pai = urljoin(BASE_URL, pai + "/")
            print(f"🔍 Acessando página do pai: {url_pai}")

            # Coleta os links da página do pai
            try:
                await page.goto(url_pai, wait_until="networkidle", timeout=20000)
                a_tags = await page.query_selector_all("a[href]")
                links_pai = set()

                for a in a_tags:
                    href = await a.get_attribute("href")
                    if href:
                        link_completo = urljoin(url_pai, href)
                        links_pai.add(link_completo)

                # Remove duplicados e ordena
                links_pai_ordenados = sorted(set(links_pai))
            except Exception as e:
                print(f"⚠️ Erro ao acessar a página do pai {url_pai}: {e}")
                links_pai_ordenados = []

            # Inicializa estrutura do pai
            resultado[pai] = {
                "url_pai": url_pai,
                "links_pai": links_pai_ordenados,
                "filhos": {}
            }

            # Coleta os links das páginas dos filhos
            for url_filho in urls_filhos:
                print(f"   ↪ Acessando filho: {url_filho}")
                try:
                    await page.goto(url_filho, wait_until="networkidle", timeout=20000)
                    a_tags = await page.query_selector_all("a[href]")
                    links_filhos = set()

                    for a in a_tags:
                        href = await a.get_attribute("href")
                        if href:
                            link_completo = urljoin(url_filho, href)
                            links_filhos.add(link_completo)

                    resultado[pai]["filhos"][url_filho] = sorted(set(links_filhos))
                except Exception as e:
                    print(f"⚠️ Erro ao acessar filho {url_filho}: {e}")
                    resultado[pai]["filhos"][url_filho] = []

        await browser.close()

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Mapeamento completo salvo em '{ARQUIVO_SAIDA}'")

asyncio.run(mapear_novos_links())
