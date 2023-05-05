import os
from time import sleep
from datetime import datetime
import os.path
from pathlib import Path

sizeLog         = None                      # VARIÁVEL DO TAMANHO DO LOG
newSizeLog      = None                      # VARIÁVEL DO TAMANHO DO LOG ATUALIZADA
robo_exe        = ''                        # NOME DO ARQUIVO EXECUTÁVEL DO ROBÔ
pre_robo_log    = ''                        # NOME DO ARQUIVO DE LOG DO ROBÔ
sleep_minutos   = 35                        # DE QUANTO EM QUANTO TEMPO O ROBÔ EXECUTARÁ A VERIFICAÇÃO

print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+f'Iniciando "{robo_exe}" pela primeira vez...')
os.popen(robo_exe)

##### A PARTIR DESTE PONTO É UM LOOPING ETERNO
while True:
    
    ##### REINICIA O ROBÔ PELO MENOS 1 VEZ AO DIA PARA CERTIFICAR QUE ESTÁ TUDO CERTO.
    if (datetime.now()).strftime('%H') == '02':
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+"REINICIALIZAÇÃO DIÁRIA "+str(robo_exe))
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+"Estarei fazendo as ações necessárias, por favor aguarde... ")        
        os.system('taskkill /F /IM '+str(robo_exe))
        os.popen(str(robo_exe))
    
    robo_log = f'{pre_robo_log}{datetime.now().strftime("%Y%m%d")}.txt' 
    print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+'Verificando '+str(robo_exe))

    ##### CAPTURA O TAMANHO ATUAL DO LOG DO ROBÔ
    try:
        newSizeLog = Path(robo_log).stat().st_size
    except:
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+'excessão - falha na busca o tamanho do log')
        pass

    ##############################################################
    ##### COMPARA O TAMANHO DO LOG ATUAL COM O DA ULTIMA VEZ QUE FEZ A VERIFICAÇÃO
    ##### CASO NÃO TENHA ALTERAÇÃO ELE JÁ REINICIA O ROBÔ
    ##### CASO O LOG ESTEJA SENDO GRAVADO NORMALMENTE, ELE VERIFICA POSTERIORMENTE.
    if sizeLog == newSizeLog:
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+"Será necessário reiniciar "+str(robo_exe))
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+"Estarei fazendo as ações necessárias, por favor aguarde... ")
        os.system('taskkill /F /IM '+str(robo_exe))
        os.popen(str(robo_exe))
    else:
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+"Não será feita nenhuma ação no momento...")
    try:
        sizeLog = Path(str(robo_log)).stat().st_size
    except:
        print (str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+'excessão - falha ao atualizar a variável do tamanho do log')
        pass
    ##############################################################
            
    print(str(datetime.now().strftime("%d/%m/%Y %H:%M:%S")+' - ')+f'''Aguardarei {sleep_minutos} minutos...\nDepois verificarei novamente se "{robo_exe}" está funcionando.''')
    print('\n---------------------------------------------\n')
    # sleep (60)
    sleep (60*sleep_minutos)