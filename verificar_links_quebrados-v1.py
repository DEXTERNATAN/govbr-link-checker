import asyncio
import json
from playwright.async_api import async_playwright

ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
BASE_URL = "https://www.gov.br/ds/"
MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"

async def verificar_links():
    with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
        estrutura = json.load(f)

    resultado = []

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        for pai, filhos in estrutura.items():
            url_pai = BASE_URL + pai
            for filho_url in filhos:
                print(f"🔎 Verificando: {filho_url}")
                status = "ok"

                try:
                    response = await page.goto(filho_url, wait_until="domcontentloaded", timeout=20000)
                    status_code = response.status if response else 0
                    content = await page.content()

                    if status_code >= 400:
                        status = f"HTTP {status_code}"
                    elif MENSAGEM_ERRO_PADRAO.lower() in content.lower():
                        status = "pagina inexistente"

                except Exception as e:
                    print(f"⚠️ Erro ao verificar {filho_url}: {e}")
                    status = "erro de carregamento"

                resultado.append({
                    "pai": pai,
                    "url_pai": url_pai,
                    "filho": filho_url,
                    "status": status
                })

        await browser.close()

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Verificação finalizada. Resultado salvo em '{ARQUIVO_SAIDA}'.")

asyncio.run(verificar_links())
