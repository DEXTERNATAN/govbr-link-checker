import asyncio
import json
from playwright.async_api import async_playwright

ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"

async def verificar_links():
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        estrutura = json.load(f)

    resultado = {}

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for pai, dados in estrutura.items():
            resultado[pai] = {
                "url_pai": dados["url_pai"],
                "links_pai": [],
                "filhos": {}
            }

            # Verifica links da página pai
            for url in dados.get("links_pai", []):
                print(f"🔍 Verificando link do pai: {url}")
                status = "ok"
                try:
                    response = await page.goto(url, wait_until="domcontentloaded", timeout=20000)
                    status_code = response.status if response else 0
                    content = await page.content()
                    if status_code >= 400:
                        status = f"HTTP {status_code}"
                    elif MENSAGEM_ERRO_PADRAO.lower() in content.lower():
                        status = "pagina inexistente"
                except Exception as e:
                    print(f"⚠️ Erro ao verificar {url}: {e}")
                    status = "erro de carregamento"
                resultado[pai]["links_pai"].append({url: status})

            # Verifica links das páginas filhas
            for filho_url, links in dados.get("filhos", {}).items():
                resultado[pai]["filhos"][filho_url] = []
                for link in links:
                    print(f"   ↪ Verificando link do filho: {link}")
                    status = "ok"
                    try:
                        response = await page.goto(link, wait_until="domcontentloaded", timeout=20000)
                        status_code = response.status if response else 0
                        content = await page.content()
                        if status_code >= 400:
                            status = f"HTTP {status_code}"
                        elif MENSAGEM_ERRO_PADRAO.lower() in content.lower():
                            status = "pagina inexistente"
                    except Exception as e:
                        print(f"⚠️ Erro ao verificar {link}: {e}")
                        status = "erro de carregamento"
                    resultado[pai]["filhos"][filho_url].append({link: status})

        await browser.close()

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Verificação finalizada. Resultado salvo em '{ARQUIVO_SAIDA}'.")

if __name__ == "__main__":
    asyncio.run(verificar_links())
