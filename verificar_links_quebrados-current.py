import asyncio
import json
from playwright.async_api import async_playwright, Page, Browser
from typing import Dict, Any, List

ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"
TIMEOUT_PADRAO = 30000  # 3 segundos
MAX_TENTATIVAS = 1

async def tentar_abrir_pagina(page: Page, url: str, tentativas: int = MAX_TENTATIVAS):
    """Tenta abrir uma página com tratamento de retries."""
    for tentativa in range(tentativas):
        try:
            response = await page.goto(url, wait_until="domcontentloaded", timeout=TIMEOUT_PADRAO)
            return response
        except Exception as e:
            print(f"   🔁 Tentativa {tentativa + 1} falhou para {url}: {e}")
            if tentativa == tentativas - 1:
                raise
            await asyncio.sleep(2)  # Espera um pouco antes de tentar novamente

async def verificar_link(page: Page, url: str) -> str:
    """Verifica o status de um único link."""
    try:
        response = await tentar_abrir_pagina(page, url)
        if response:
            status_code = response.status
            if status_code >= 400:
                return f"HTTP {status_code}"
            content = await page.content()
            if MENSAGEM_ERRO_PADRAO.lower() in content.lower():
                return "pagina inexistente"
            return "ok"
        else:
            return "sem resposta"
    except Exception as e:
        return "erro de carregamento"

async def verificar_links():
    """Função principal para verificar os links com contador de progresso."""
    try:
        with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
            estrutura: Dict[str, Dict[str, Any]] = json.load(f)
    except FileNotFoundError:
        print(f"Erro: Arquivo '{ARQUIVO_ENTRADA}' não encontrado.")
        return
    except json.JSONDecodeError:
        print(f"Erro: Falha ao decodificar JSON do arquivo '{ARQUIVO_ENTRADA}'.")
        return

    resultado: Dict[str, Dict[str, Any]] = {}
    total_links = 0
    for dados in estrutura.values():
        total_links += len(dados.get("links_pai", []))
        for links_filho in dados.get("filhos", {}).values():
            total_links += len(links_filho)

    links_verificados = 0

    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch()
        page: Page = await browser.new_page()

        for pai, dados in estrutura.items():
            resultado[pai] = {
                "url_pai": dados["url_pai"],
                "links_pai": [],
                "filhos": {}
            }

            # Verifica links da página pai de forma assíncrona
            links_pai = dados.get("links_pai", [])
            num_links_pai = len(links_pai)
            for i, url in enumerate(links_pai):
                print(f"🔍 Verificando link do pai ({i + 1}/{num_links_pai}, Total: {links_verificados + 1}/{total_links}): {url}")
                status = await verificar_link(page, url)
                resultado[pai]["links_pai"].append({url: status})
                links_verificados += 1

            # Verifica links das páginas filhas de forma assíncrona
            filhos = dados.get("filhos", {})
            resultado[pai]["filhos"] = {}
            for filho_url, links_filho in filhos.items():
                resultado[pai]["filhos"][filho_url] = []
                num_links_filho = len(links_filho)
                for i, link in enumerate(links_filho):
                    print(f"   ↪ Verificando link do filho ({i + 1}/{num_links_filho}, Total: {links_verificados + 1}/{total_links}): {link}")
                    status = await verificar_link(page, link)
                    resultado[pai]["filhos"][filho_url].append({link: status})
                    links_verificados += 1

        await browser.close()

    try:
        with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=2)
        print(f"\n✅ Verificação finalizada. Resultado salvo em '{ARQUIVO_SAIDA}'.")
    except IOError:
        print(f"Erro: Não foi possível escrever no arquivo '{ARQUIVO_SAIDA}'.")

if __name__ == "__main__":
    asyncio.run(verificar_links())

# OLD CODE LENTO DEMAIS
# import asyncio
# import json
# from playwright.async_api import async_playwright

# ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
# ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
# MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"
# TIMEOUT_PADRAO = 40000  # 40 segundos
# MAX_TENTATIVAS = 2

# async def tentar_abrir_pagina(page, url, tentativas=MAX_TENTATIVAS):
#     for tentativa in range(tentativas):
#         try:
#             return await page.goto(url, wait_until="load", timeout=TIMEOUT_PADRAO)
#         except Exception as e:
#             if tentativa == tentativas - 1:
#                 raise e
#             print(f"   🔁 Tentativa {tentativa + 1} falhou para {url}, tentando novamente...")

# async def verificar_links():
#     with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
#         estrutura = json.load(f)

#     resultado = {}

#     async with async_playwright() as p:
#         browser = await p.chromium.launch()
#         page = await browser.new_page()

#         for pai, dados in estrutura.items():
#             resultado[pai] = {
#                 "url_pai": dados["url_pai"],
#                 "links_pai": [],
#                 "filhos": {}
#             }

#             # Verifica links da página pai
#             for url in dados.get("links_pai", []):
#                 print(f"🔍 Verificando link do pai: {url}")
#                 status = "ok"
#                 try:
#                     response = await tentar_abrir_pagina(page, url)
#                     status_code = response.status if response else 0
#                     content = await page.content()
#                     if status_code >= 400:
#                         status = f"HTTP {status_code}"
#                     elif MENSAGEM_ERRO_PADRAO.lower() in content.lower():
#                         status = "pagina inexistente"
#                 except Exception as e:
#                     print(f"⚠️ Erro ao verificar {url}: {e}")
#                     status = "erro de carregamento"
#                 resultado[pai]["links_pai"].append({url: status})

#             # Verifica links das páginas filhas
#             for filho_url, links in dados.get("filhos", {}).items():
#                 resultado[pai]["filhos"][filho_url] = []
#                 for link in links:
#                     print(f"   ↪ Verificando link do filho: {link}")
#                     status = "ok"
#                     try:
#                         response = await tentar_abrir_pagina(page, link)
#                         status_code = response.status if response else 0
#                         content = await page.content()
#                         if status_code >= 400:
#                             status = f"HTTP {status_code}"
#                         elif MENSAGEM_ERRO_PADRAO.lower() in content.lower():
#                             status = "pagina inexistente"
#                     except Exception as e:
#                         print(f"⚠️ Erro ao verificar {link}: {e}")
#                         status = "erro de carregamento"
#                     resultado[pai]["filhos"][filho_url].append({link: status})

#         await browser.close()

#     with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
#         json.dump(resultado, f, ensure_ascii=False, indent=2)

#     print(f"\n✅ Verificação finalizada. Resultado salvo em '{ARQUIVO_SAIDA}'.")

# if __name__ == "__main__":
#     asyncio.run(verificar_links())
