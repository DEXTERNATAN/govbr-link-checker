import asyncio
import json
from urllib.parse import urljoin
from collections import defaultdict
from playwright.async_api import async_playwright

#v3
BASE_URL = "https://www.gov.br/ds/"

#v4
# BASE_URL = "https://www.gov.br/ds/"

# V3 - https://www.gov.br/ds/
# V4 - https://next-ds.estaleiro.serpro.gov.br/

# Estrutura intermediária
hierarquia = defaultdict(lambda: {"filhos": {}})

async def extrair_links():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(BASE_URL, wait_until="networkidle")

        a_tags = await page.query_selector_all("a[href]")
        for a in a_tags:
            href = await a.get_attribute("href")
            if href:
                full_url = urljoin(BASE_URL, href)

                if full_url.startswith(BASE_URL):
                    caminho = full_url.replace(BASE_URL, "").strip("/")
                    partes = [p for p in caminho.split("/") if p]

                    if len(partes) == 1:
                        pai = partes[0]
                        hierarquia[pai]  # garante entrada
                    elif len(partes) >= 2:
                        pai = partes[0]
                        filho = "/".join(partes[1:])
                        hierarquia[pai]["filhos"][filho] = {
                            "url": f"{BASE_URL}{pai}/{filho}"
                        }

        await browser.close()

    # Gera o resultado no formato desejado
    resultado_final = []
    for pai, dados in hierarquia.items():
        resultado_final.append({
            pai: [
                {
                    "filhos": {k: v for k, v in sorted(dados["filhos"].items())}
                }
            ]
        })

    with open("links_apenas_filhos.json", "w", encoding="utf-8") as f:
        json.dump(resultado_final, f, ensure_ascii=False, indent=2)

    print("✅ Arquivo 'links_apenas_filhos.json' gerado com sucesso.")

asyncio.run(extrair_links())
