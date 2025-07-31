from configparser import ConfigParser
import datetime
import os
import sys
import time
from src.rotinas import log
from src.comAPI import send_teams_message
import datetime
# from TeamsInt import EnviaComunicado

cfg = ConfigParser()

if hasattr(sys, '_MEIPASS'): #Captura arquivo no diretorio atual ou no anterior (Dev/Prod)
    config_path = os.path.join(sys._MEIPASS, "config.ini")
else:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")  
try:
    with open(config_path) as f:
        cfg.read_file(f)
except FileNotFoundError:
    print(f"Arquivo não encontrado: {config_path}")

local = cfg.get('DEFAULT','LOCALIDADE')
# Comunicação
api = cfg.get('COM','API')
apis = api.split(',')
canais = cfg.get('COM','CANAL')
canaisLs = [int(canal) for canal in canais.split(',')]
key = cfg.get('COM','KEY')

titulo = f'Aviso automatizado - {local}'

def EnviaMSG(mensagem, falha):
    try:
        # resposta = ""
        # Obter a data e hora atuais
        data_hora_atual = datetime.datetime.now()
        data_formatada = data_hora_atual.strftime("%d de %B de %Y")
        hora_formatada = data_hora_atual.strftime("%H:%M")
        # Mensagem da Dona Odete com um marcador de posição para o aviso
        recado = ''
        if falha == 0:#Percentual abaixo
            recado = f"""
Olá, meus docinhos!  
   
Aqui quem fala é a Vovó Odete.  
   
Parece que o ELOS resolveu tirar uma soneca técnica.  
   
**Detalhes do ocorrido:**  
- **Data:** {data_formatada}  
- **Horário:** às {hora_formatada}  
- {mensagem}  
   
Se precisarem, estarei aqui na cozinha, com chá quentinho e biscoitos.  
   
Com muito carinho,  
**Vovó Odete**
            """
        if falha == 1:#Reestabelecimento
            recado = f"""
Olá, meus docinhos!  
   
Aqui quem fala é a Vovó Odete. Aceita um biscoito?  
   
Venho trazer uma boa notícia.  
   
**Detalhes do ocorrido:**  
- **Data:** {data_formatada}  
- **Horário:** às {hora_formatada}  
- {mensagem}  
   
Se precisarem, estarei aqui na cozinha, com chá quentinho e biscoitos.  
   
Com muito carinho,  
**Vovó Odete**
            """
        if falha == 2:#Falha sistêmica
            recado = f"""
Olá, meus amores!  
   
Aqui é a vovó Odete, tive um probleminha aqui na cozinha. Vou precisar da ajuda de vocês.  
   
**Detalhes do ocorrido:**  
- **Data:** {data_formatada}  
- **Horário:** às {hora_formatada}  
- {mensagem}  
   
Quando puderem, deem uma passadinha aqui!  
   
Com muito carinho,  
**Vovó Odete**
            """
            #Rota de comunicação

        if api: #Se possuir url de API
            i = 0
            while (i <= len(apis)):
                for canal in canaisLs:
                    payload = {
                        "titulo": titulo,
                        "msg": recado,
                        "canal": int(canal),
                        "key": key
                    }
                    resposta = send_teams_message(payload, apis[i])
                    if resposta != 'true':#Se nao comunicou tenta o proximo
                        log('erro', resposta)
                        if len(apis) == 1:
                            i = len(apis) + 1
                            break
                        elif i >= len(apis): # Se ultima url da lista
                            i = len(apis) + 1
                            break
                        else: #Se nao, tenta proximo
                            i = i+1
                            time.sleep(5)
                    else: #Se comunicou encerra loop
                        i = len(apis) + 1
                        break

        # else:#Padrão para teams
        #     if urlTeams:
        #         ret = EnviaComunicado(urlTeams, recado, titulo)
        #         if ret:
        #             log('erro', f'[COMUNICACAO] - {ret}')
        #     else:
        #         print(f'[COMUNICACAO] - Local: {local} {mensagem}')
    except Exception as ex:
        log('erro', f'[COMUNICACAO] - {ex}')
        print(f'[COMUNICACAO] - {ex}')