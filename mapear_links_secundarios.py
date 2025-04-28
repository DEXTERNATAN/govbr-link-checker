import asyncio
import json
from urllib.parse import urljoin
from playwright.async_api import async_playwright

ARQUIVO_ENTRADA = "links_apenas_filhos.json"
ARQUIVO_SAIDA = "novos_links_por_pagina.json"
#BASE_URL = "https://www.gov.br/ds/"
BASE_URL = "https://next-ds.estaleiro.serpro.gov.br/"

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

            dados_pai = {
                "url_pai": url_pai,
                "links_pai": [],
                "tempo_pai": 0,
                "erro_pai": {
                    "ocorreu": False,
                    "mensagem": "",
                    "tipo": ""
                },
                "filhos": {}
            }

            # Coleta os links da página do pai dentro da .main-content
            try:
                inicio = asyncio.get_event_loop().time()
                await page.goto(url_pai, wait_until="networkidle", timeout=20000)
                fim = asyncio.get_event_loop().time()
                dados_pai["tempo_pai"] = round(fim - inicio, 3)

                main_content = await page.query_selector(".main-content")
                a_tags = await main_content.query_selector_all("a[href]") if main_content else []
                links_pai = set()

                for a in a_tags:
                    href = await a.get_attribute("href")
                    if href:
                        link_completo = urljoin(url_pai, href)
                        links_pai.add(link_completo)

                dados_pai["links_pai"] = sorted(set(links_pai))
            except Exception as e:
                fim = asyncio.get_event_loop().time()
                dados_pai["tempo_pai"] = round(fim - inicio, 3)
                print(f"⚠️ Erro ao acessar a página do pai {url_pai}: {e}")
                dados_pai["erro_pai"] = {
                    "ocorreu": True,
                    "mensagem": str(e),
                    "tipo": type(e).__name__
                }

            # Coleta os links das páginas dos filhos dentro da .main-content
            for url_filho in urls_filhos:
                print(f"   ↪ Acessando filho: {url_filho}")
                filho_info = {
                    "links": [],
                    "tempo": 0,
                    "erro": {
                        "ocorreu": False,
                        "mensagem": "",
                        "tipo": ""
                    }
                }
                try:
                    inicio = asyncio.get_event_loop().time()
                    await page.goto(url_filho, wait_until="networkidle", timeout=20000)
                    fim = asyncio.get_event_loop().time()
                    filho_info["tempo"] = round(fim - inicio, 3)

                    main_content = await page.query_selector(".main-content")
                    a_tags = await main_content.query_selector_all("a[href]") if main_content else []
                    links_filhos = set()

                    for a in a_tags:
                        href = await a.get_attribute("href")
                        if href:
                            link_completo = urljoin(url_filho, href)
                            links_filhos.add(link_completo)

                    filho_info["links"] = sorted(set(links_filhos))
                except Exception as e:
                    fim = asyncio.get_event_loop().time()
                    filho_info["tempo"] = round(fim - inicio, 3)
                    print(f"⚠️ Erro ao acessar filho {url_filho}: {e}")
                    filho_info["erro"] = {
                        "ocorreu": True,
                        "mensagem": str(e),
                        "tipo": type(e).__name__
                    }

                dados_pai["filhos"][url_filho] = filho_info

            resultado[pai] = dados_pai

        await browser.close()

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Mapeamento completo salvo em '{ARQUIVO_SAIDA}'")

asyncio.run(mapear_novos_links())
