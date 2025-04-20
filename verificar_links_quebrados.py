import json
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.http import Request
from scrapy.spiders import Spider
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError
from typing import Dict, Any, List, Optional

ARQUIVO_ENTRADA = "novos_links_por_pagina.json"
ARQUIVO_SAIDA = "verificacao_links_quebrados.json"
MENSAGEM_ERRO_PADRAO = "Desculpe, mas esta página não existe…"
TIMEOUT_PADRAO = 120  # Aumentado para 2 minutos (era 60 segundos)
MAX_TENTATIVAS = 3   # Aumentado para 3 tentativas (era 2)

# User-Agent compatível com navegadores reais
USER_AGENT_PADRAO = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

class LinkVerificador(Spider):
    name = 'verificador_links'
    
    def __init__(self, estrutura_dados=None, *args, **kwargs):
        super(LinkVerificador, self).__init__(*args, **kwargs)
        self.estrutura_dados = estrutura_dados
        self.resultado = {}
        self.requests_pendentes = {}  # Para rastrear solicitações
        self.logger.info("✅ Iniciando verificação com timeout de %s segundos e %s tentativas", TIMEOUT_PADRAO, MAX_TENTATIVAS)
        
    def start_requests(self):
        # Itera por cada seção pai na estrutura de dados
        for pai, dados in self.estrutura_dados.items():
            self.resultado[pai] = {
                "url_pai": dados.get("url_pai"),
                "tempo_pai": dados.get("tempo_pai", 0),
                "erro_pai": dados.get("erro_pai", {}),
                "links_pai": [],
                "filhos": []
            }
            
            # Verifica se já existe um erro no pai
            has_error = False
            if self.resultado[pai]["erro_pai"] and self.resultado[pai]["erro_pai"].get("ocorreu"):
                has_error = True
            
            # Processa links do pai
            for url in dados.get("links_pai", []):
                self.logger.info(f"🔗 Verificando link do pai: {url}")
                # Adiciona à lista de links pendentes
                request_id = f"pai_{pai}_{url}"
                self.requests_pendentes[request_id] = {"pai": pai, "tipo": "link_pai", "url": url}
                
                # Envia a requisição com timeout específico
                yield Request(
                    url=url,
                    callback=self.parse_response,
                    errback=self.handle_error,
                    meta={
                        "request_id": request_id,
                        "download_timeout": TIMEOUT_PADRAO
                    },
                    headers={
                        "User-Agent": USER_AGENT_PADRAO,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                        "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                        "Cache-Control": "no-cache",
                        "Pragma": "no-cache"
                    },
                    dont_filter=True
                )
            
            # Processa filhos
            filhos_info = dados.get("filhos", {})
            for url_filho, filho_data in filhos_info.items():
                filho_obj = {
                    "url": url_filho,
                    "tempo": filho_data.get("tempo", 0),
                    "erro": filho_data.get("erro", {}),
                    "subfilhos": []
                }
                
                # Verifica se há erro no filho
                if filho_obj["erro"] and filho_obj["erro"].get("ocorreu"):
                    has_error = True
                
                # Adiciona o filho ao resultado
                self.resultado[pai]["filhos"].append(filho_obj)
                
                # Processa subfilhos
                for link in filho_data.get("links", []):
                    self.logger.info(f"    ↪ Verificando subfilho: {link}")
                    # Adiciona à lista de links pendentes
                    request_id = f"filho_{pai}_{url_filho}_{link}"
                    self.requests_pendentes[request_id] = {
                        "pai": pai, 
                        "tipo": "subfilho", 
                        "url": link,
                        "url_filho": url_filho
                    }
                    
                    # Envia a requisição com timeout específico
                    yield Request(
                        url=link,
                        callback=self.parse_response,
                        errback=self.handle_error,
                        meta={
                            "request_id": request_id,
                            "download_timeout": TIMEOUT_PADRAO
                        },
                        headers={
                            "User-Agent": USER_AGENT_PADRAO,
                            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                            "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
                            "Cache-Control": "no-cache",
                            "Pragma": "no-cache"
                        },
                        dont_filter=True
                    )
            
            # Inicializa a flag de erro
            if "erro_pai" not in self.resultado[pai]:
                self.resultado[pai]["erro_pai"] = {}
            self.resultado[pai]["erro_pai"]["erro_links_pai"] = has_error
    
    def parse_response(self, response):
        """Processa a resposta HTTP bem-sucedida."""
        request_id = response.meta.get("request_id")
        info = self.requests_pendentes.pop(request_id, None)
        
        if info:
            status_code = response.status
            result = self.processar_status(status_code, response)
            
            # Verifica se a página contém mensagem de erro padrão
            if result["status"] == "ok" and MENSAGEM_ERRO_PADRAO.lower() in response.text.lower():
                result = {
                    "status": "pagina inexistente", 
                    "http_status": status_code, 
                    "detalhes": "Página retornou 200 mas contém mensagem de erro"
                }
            
            # Atualiza o resultado conforme o tipo de link
            if info["tipo"] == "link_pai":
                self.resultado[info["pai"]]["links_pai"].append({"url": info["url"], **result})
                # Atualiza flag de erro se necessário
                if result["status"] != "ok":
                    self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
            
            elif info["tipo"] == "subfilho":
                # Encontra o filho correto para adicionar o subfilho
                for filho in self.resultado[info["pai"]]["filhos"]:
                    if filho["url"] == info["url_filho"]:
                        filho["subfilhos"].append({"url": info["url"], **result})
                        # Atualiza flag de erro se necessário
                        if result["status"] != "ok":
                            self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
                        break
    
    def handle_error(self, failure):
        """Trata falhas de requisição."""
        request = failure.request
        request_id = request.meta.get("request_id")
        info = self.requests_pendentes.pop(request_id, None)
        
        if info:
            # Determina o tipo de erro
            result = self.classificar_erro(failure)
            
            # Atualiza o resultado conforme o tipo de link
            if info["tipo"] == "link_pai":
                self.resultado[info["pai"]]["links_pai"].append({"url": info["url"], **result})
                # Atualiza flag de erro
                self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
            
            elif info["tipo"] == "subfilho":
                # Encontra o filho correto para adicionar o subfilho
                for filho in self.resultado[info["pai"]]["filhos"]:
                    if filho["url"] == info["url_filho"]:
                        filho["subfilhos"].append({"url": info["url"], **result})
                        # Atualiza flag de erro
                        self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
                        break
    
    def processar_status(self, http_status, response):
        """Classifica a resposta com base no código HTTP."""
        # Status code 200-299 (Success)
        if 200 <= http_status < 300:
            return {"status": "ok", "http_status": http_status}
        
        # Status code 300-399 (Redirection)
        elif 300 <= http_status < 400:
            return {"status": f"HTTP {http_status} (redirecionamento)", "http_status": http_status, "detalhes": "Redirecionamento"}
        
        # Status code 400-499 (Client Error)
        elif 400 <= http_status < 500:
            if http_status == 404:
                return {"status": "HTTP 404 (não encontrado)", "http_status": http_status, "detalhes": "Página não encontrada"}
            elif http_status == 403:
                return {"status": "HTTP 403 (proibido)", "http_status": http_status, "detalhes": "Acesso proibido"}
            elif http_status == 401:
                return {"status": "HTTP 401 (não autorizado)", "http_status": http_status, "detalhes": "Não autorizado"}
            else:
                return {"status": f"HTTP {http_status} (erro cliente)", "http_status": http_status, "detalhes": "Erro do cliente"}
        
        # Status code 500-599 (Server Error)
        elif 500 <= http_status < 600:
            return {"status": f"HTTP {http_status} (erro servidor)", "http_status": http_status, "detalhes": "Erro do servidor"}
        
        # Any other status code
        else:
            return {"status": f"HTTP {http_status}", "http_status": http_status, "detalhes": "Status HTTP desconhecido"}
    
    def classificar_erro(self, failure):
        """Classifica o tipo de erro ocorrido durante a requisição."""
        erro_msg = str(failure.value).lower()
        
        if failure.check(DNSLookupError):
            return {"status": "dns não resolvido", "http_status": None, "detalhes": "Nome do domínio não pôde ser resolvido"}
        elif failure.check(TimeoutError, TCPTimedOutError) or "timeout" in erro_msg:
            return {"status": "timeout", "http_status": None, "detalhes": f"Tempo limite de {TIMEOUT_PADRAO}s excedido"}
        elif failure.check(ConnectionRefusedError) or "connection refused" in erro_msg:
            return {"status": "conexão recusada", "http_status": None, "detalhes": "Servidor recusou a conexão"}
        elif "SSL" in str(failure.value) or "ssl" in erro_msg:
            return {"status": "erro SSL", "http_status": None, "detalhes": "Erro de protocolo SSL/TLS"}
        elif "HTTP 2" in str(failure.value) or "HTTP2" in str(failure.value) or "http2" in erro_msg:
            return {"status": "erro HTTP2", "http_status": None, "detalhes": "Erro de protocolo HTTP/2. O site pode estar bloqueando automações."}
        elif "no response" in erro_msg or "sem resposta" in erro_msg:
            return {"status": "sem resposta", "http_status": None, "detalhes": "Servidor não respondeu no tempo esperado"}
        else:
            return {"status": "erro de carregamento", "http_status": None, "detalhes": f"Erro: {str(failure.value)[:100]}"}
    
    def closed(self, reason):
        """Método chamado quando o spider termina."""
        self.logger.info("\n✅ Verificação de links finalizada. Salvando resultados...")
        
        # Verifica se há requisições pendentes e as marca como "sem resposta"
        if self.requests_pendentes:
            self.logger.warning(f"⚠️ Ainda existem {len(self.requests_pendentes)} requisições pendentes")
            for request_id, info in self.requests_pendentes.items():
                self.logger.warning(f"  ↪ Requisição pendente: {info['url']}")
                
                result = {
                    "status": "sem resposta", 
                    "http_status": None, 
                    "detalhes": f"O servidor não respondeu após {TIMEOUT_PADRAO}s e {MAX_TENTATIVAS} tentativas"
                }
                
                # Adiciona ao resultado
                if info["tipo"] == "link_pai":
                    self.resultado[info["pai"]]["links_pai"].append({"url": info["url"], **result})
                    self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
                elif info["tipo"] == "subfilho":
                    for filho in self.resultado[info["pai"]]["filhos"]:
                        if filho["url"] == info["url_filho"]:
                            filho["subfilhos"].append({"url": info["url"], **result})
                            self.resultado[info["pai"]]["erro_pai"]["erro_links_pai"] = True
                            break
        
        try:
            with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
                json.dump(self.resultado, f, ensure_ascii=False, indent=2)
            self.logger.info(f"✅ Resultado salvo em '{ARQUIVO_SAIDA}'")
        except IOError as e:
            self.logger.error(f"❌ Erro ao salvar o arquivo '{ARQUIVO_SAIDA}': {e}")

def verificar_links():
    # Carrega os dados do arquivo JSON
    try:
        with open(ARQUIVO_ENTRADA, "r", encoding="utf-8") as f:
            estrutura = json.load(f)
    except Exception as e:
        print(f"❌ Erro ao carregar o arquivo de entrada: {e}")
        return
    
    # Configuração do processo Scrapy
    process = CrawlerProcess(settings={
        'USER_AGENT': USER_AGENT_PADRAO,
        'DOWNLOAD_TIMEOUT': TIMEOUT_PADRAO,
        'RETRY_TIMES': MAX_TENTATIVAS,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 522, 524, 408, 429, 403],  # Códigos para tentar novamente
        'CONCURRENT_REQUESTS': 8,  # Reduzido para evitar sobrecarga (era 16)
        'CONCURRENT_REQUESTS_PER_DOMAIN': 4, # Limite de requisições por domínio
        'DOWNLOAD_DELAY': 0.5,     # Aumentado para reduzir probabilidade de bloqueio
        'LOG_LEVEL': 'INFO',
        'COOKIES_ENABLED': True,
        'ROBOTSTXT_OBEY': False,
        # Middlewares para tratamento de erros e redirecionamentos
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': 500,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 800,
            'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
        },
        # Timeout mais agressivo para evitar requisições pendentes
        'DOWNLOAD_MAXSIZE': 10485760,  # 10MB de limite máximo
        'DNS_TIMEOUT': 60,
        'CONNECT_TIMEOUT': 60,
    })
    
    # Executa o spider
    process.crawl(LinkVerificador, estrutura_dados=estrutura)
    process.start()  # O processo é bloqueante, vai esperar até terminar

if __name__ == "__main__":
    verificar_links()
