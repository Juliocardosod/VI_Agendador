# with open('agenda.txt', 'r') as arquivo:
#     agenda = [linha.strip() for linha in arquivo if linha.strip()]


# for tarefa in agenda:
#     campos = tarefa.split(';')
#     print(f'Nome Tarefa: {campos[0]}, Caminho: {campos[1]}, Horários: {campos[2]}')

import configparser
import os
import threading
import time
from datetime import datetime, timedelta
import subprocess
from src.rotinas import log, limpaLogTH
from src.com import EnviaMSG

versao = '0.2'

config_path = os.path.join(os.path.dirname(__file__), "config.ini")

try:
    with open(config_path, 'r', encoding='utf-8') as f:
        cfg = configparser.ConfigParser()
        cfg.read_file(f)
except Exception as ex:
    log('erro', f'[CFG] {ex}')

debug = cfg.getboolean('DEFAULT','DEBUG')

def carregar_agenda(caminho_arquivo):#Carrega arquivo tarefas
    agenda = []
    with open(caminho_arquivo, 'r') as f:
        for linha in f:
            nome, caminho, tipo, dados = linha.strip().split(';')
            if tipo == 'horario':
                horarios = [h.strip() for h in dados.split(',')]
                agenda.append({'nome': nome, 'caminho': caminho, 'tipo': tipo, 'horarios': horarios})
            elif tipo == 'intervalo':
                intervalo = int(dados.strip())
                proxima_execucao = datetime.now()
                agenda.append({'nome': nome, 'caminho': caminho, 'tipo': tipo, 'intervalo': intervalo, 'proxima': proxima_execucao})
    return agenda

def executar_tarefa(tarefa): #Thread
    try:
        subprocess.Popen(f'start "" "{tarefa["caminho"]}"', shell=True)
        # subprocess.Popen(tarefa['caminho'])
        if debug:
            log('info', f"Executando {tarefa['nome']}")
            print(f"Executando {tarefa['nome']}")
    except Exception as ex:
        log('erro', f"[TAREFA] - {ex}")
        print(f"[TAREFA] - {ex}")
        EnviaMSG(f"[TAREFA] - {ex}", 2)

def executar_agenda(agenda):
    executados_horario = set()
    while True:
        try:
            agora = datetime.now().strftime('%H:%M')
            agora_dt = datetime.now()
            for tarefa in agenda:
                if tarefa['tipo']:
                    if tarefa['tipo'] == 'horario':
                        for h in tarefa['horarios']:
                            if agora == h and (tarefa['nome'], h) not in executados_horario:
                                if debug:
                                    print(f"Executando {tarefa['nome']} às {h}")
                                    log('info', f"Executando {tarefa['nome']} às {h}")
                                # subprocess.Popen(tarefa['caminho'])
                                # executados_horario.add((tarefa['nome'], h))
                                t = threading.Thread(target=executar_tarefa, args=(tarefa,))
                                t.start()
                                executados_horario.add((tarefa['nome'], h))

                    elif tarefa['tipo'] == 'intervalo':
                        if agora_dt >= tarefa['proxima']:
                            if debug:
                                print(f"Executando {tarefa['nome']} por intervalo de {tarefa['intervalo']} minutos")
                                log('info', f"Executando {tarefa['nome']} por intervalo de {tarefa['intervalo']} minutos")
                            # subprocess.Popen(tarefa['caminho'])
                            # tarefa['proxima'] = agora_dt + timedelta(minutes=tarefa['intervalo'])
                            t = threading.Thread(target=executar_tarefa, args=(tarefa,))
                            t.start()
                            tarefa['proxima'] = agora_dt + timedelta(minutes=tarefa['intervalo'])

        except Exception as ex:
            print(ex)
            log('erro', f'[AGENDA] - {ex}')
            EnviaMSG(f'[AGENDA] - {ex}', 2)
        finally:
            time.sleep(30)

log('info', f'Iniciando aplicação V {versao} ')
try:
    logTH = threading.Thread(target=limpaLogTH, args=())
    logTH.start() #limpeza de log

    agenda = carregar_agenda('agenda.txt')
    executar_agenda(agenda)
except Exception as ex:
    print(ex)
    log('erro', f'[LOOP] - {ex}')
    EnviaMSG(f'[LOOP] - {ex}', 2)
