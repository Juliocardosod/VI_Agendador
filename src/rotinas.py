from configparser import ConfigParser
import logging
from datetime import date
import os
import time
import sys

logger = logging.getLogger('MainLogger')
logger.setLevel(logging.INFO)

cfg = ConfigParser()
# cfg.read_file(open(os.path.join(os.path.dirname(__file__),"config.ini")))

if hasattr(sys, '_MEIPASS'): #Captura arquivo no diretorio atual ou no anterior (Dev/Prod)
    config_path = os.path.join(sys._MEIPASS, "config.ini")
else:
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.ini")  

try:
    with open(config_path) as f:
        cfg.read_file(f)
except FileNotFoundError:
    print(f"Arquivo não encontrado: {config_path}")


diasLog = cfg.getint('DEFAULT','DIAS_LOG')
logDir = cfg.get('DEFAULT','LOG_DIR')

if not os.path.exists("LOG"): #Criar diretório de log
        os.makedirs("LOG")

def log(tipo, mensagem):#Escreve em arquivo log
        try:
            fh = logging.FileHandler("{}\LogMonitor_{}.log".format(logDir,
            str(date.today())))
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            fh.setFormatter(formatter)
            logger.addHandler(fh)

            if tipo == 'info':
                logger.info(mensagem)
            elif tipo == 'erro':
                logger.error(mensagem)

            logger.removeHandler(fh)
        except Exception as ex:
            print(f"Erro: {ex}")

def limpaLogTH(): #Limpeza de LOGs
    while True:
        now = time.time()
        lista = []
        try:

            for filename in os.listdir(logDir):
                filestamp = os.stat(os.path.join(logDir, filename)).st_mtime
                filecompare = now - diasLog * 86400
                if  filestamp < filecompare:
                    lista.append(os.path.join(logDir, filename))

            for item in lista:
                # Log('info', f'Apagando arquivo log: {item}')
                os.remove(item)

        except Exception as ex:
            print(ex)
            # log('erro', ex)
        finally:
            time.sleep(43200) #Limpeza a cada 12hrs