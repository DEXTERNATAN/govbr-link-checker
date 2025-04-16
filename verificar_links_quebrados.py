import asyncio
import json
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Any, List, Optional

ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"
TIMEOUT_PADRAO = 30000
MAX_TENTATIVAS = 1

async def tentar_abrir_pagina(page: Page, url: str, tentativas: int = MAX_TENTATIVAS):
    for tentativa in range(tentativas):
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_PADRAO)
            return response
        except Exception as e:
            print(f"   🔁 Tentativa {tentativa + 1} falhou para {url}: {e}")
            if tentativa == tentativas - 1:
                raise
            await asyncio.sleep(2)

async def verificar_link(page: Page, url: str) -> Dict[str, Any]:
    """Retorna um dicionário com status textual e código HTTP."""
    try:
        response = await tentar_abrir_pagina(page, url)
        if response:
            http_status = response.status
            content = await page.content()
            if http_status >= 400:
                return { "status": f"HTTP {http_status}", "http_status": http_status }
            if MENSAGEM_ERRO_PADRAO.lower() in content.lower():
                return { "status": "pagina inexistente", "http_status": http_status }
            return { "status": "ok", "http_status": http_status }
        else:
            return { "status": "sem resposta", "http_status": None }
    except Exception:
        return { "status": "erro de carregamento", "http_status": None }

async def verificar_links():
    try:
        with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
            estrutura: Dict[str, Any] = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar o arquivo de entrada: {e}")
        return

    resultado = {}

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch()
        page: Page = await browser.new_page()

        for pai, dados in estrutura.items():
            print(f"🔍 Verificando seção pai: {pai}")
            resultado[pai] = {
                "url_pai": dados.get("url_pai"),
                "tempo_pai": dados.get("tempo_pai", 0),
                "erro_pai": dados.get("erro_pai", {}),
                "links_pai": [],
                "filhos": []
            }

            # Verifica links do pai
            for i, url in enumerate(dados.get("links_pai", [])):
                print(f"   🔗 Link do pai ({i+1}/{len(dados['links_pai'])}): {url}")
                res = await verificar_link(page, url)
                resultado[pai]["links_pai"].append({ "url": url, **res })

            # Verifica filhos
            filhos_info = dados.get("filhos", {})
            for idx, (url_filho, filho_data) in enumerate(filhos_info.items()):
                print(f"   ↪ Verificando filho {idx+1}: {url_filho}")
                filho_obj = {
                    "url": url_filho,
                    "tempo": filho_data.get("tempo", 0),
                    "erro": filho_data.get("erro", {}),
                    "subfilhos": []
                }

                for j, link in enumerate(filho_data.get("links", [])):
                    print(f"      ↪ Subfilho ({j+1}/{len(filho_data['links'])}): {link}")
                    res = await verificar_link(page, link)
                    filho_obj["subfilhos"].append({ "url": link, **res })

                resultado[pai]["filhos"].append(filho_obj)

        await browser.close()

    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Verificação finalizada. Resultado salvo em '{ARQUIVO_SAIDA}'")
    except IOError:
        print(f"Erro: Não foi possível salvar o arquivo '{ARQUIVO_SAIDA}'.")

if __name__ == "__main__":
    asyncio.run(verificar_links())
