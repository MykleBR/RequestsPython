
from config import Config, LogType, TransferStatus
from datetime import datetime,time,timedelta
from pkg_resources import resource_filename
from cryptography.fernet import Fernet
from tkinter import messagebox
from guipart import GuiPart
from site_exemplo import Exemplo
from bd_exemplo import BdExemplo
from queue import Queue
from time import sleep
from glob import glob
import threading
import tkinter
import os

banco   = BdExemplo()

class Application():
    nextCapture = None # * GRAVA HORARIO DA PROXIMA EXECUÇÃO
    
    def __init__(self,master):
        self.master         = master
        self.queue          = Queue()
        self.gui            = GuiPart(master,self.queue)
        self.running        = 1
        self.th_capture     = threading.Thread(target=self.capture)
        self.site_exemplo   = Exemplo()
        
    def decrypta(self,senha):
        key = b'N-nMdHttV7-iyB_FxR9Q6NlfkEd1QGp12iVfn-RPEZY='
        f = Fernet(key)
        dec = f.decrypt(senha)
        dec = str(str(dec).replace("b'", "")).replace("'",'')
        return dec        
    
    def make_login(self,startThread:bool=True):
        """Metodo que realiza login no site exemplo.com utilizano as informacoes da tela

        Returns:
            None: Nao ha retorno da funcao, apenas exibe mensagens em caso de falhas
        """
        exemplo = BdExemplo()
        gestor = exemplo.get_gestor()
        if gestor == None:
            self.registrando('Erro, Não foi encontrado gestor válido!','RED','ANO')
        else:    
            gestor_user = gestor[0]
            gestor_pass = self.decrypta(gestor[1].encode('ascii')) 
            self.registrando('Acessando http://exemplo.com, por favor, aguarde...','BLACK','SEMANA')
            login = self.site_exemplo.make_login(gestor_user,gestor_pass)
            if login==0:
                self.registrando('Falha, senha de gestor inválida','RED','ANO')
                exemplo.invalid_gestor(gestor_user)
                self.registrando('Buscando próximo gestor...','BLACK','ANO')
                self.make_login()
            elif login==1:
                if startThread==True:
                    self.th_capture.start()
            else:
                messagebox.showerror(title="Robo informa:",message="Ocorreu um erro no servidor que impossibilitou o acesso!")
                self.registrando(str(self.site_exemplo.get_last_error()),'RED','ANO')
            return None

    def check_life(self):
        """ Verifica se a janela ainda está viva, em caso negativo finaliza o processo """
        while True:
            try:
                self.master.state()
            except:
                meu_pid = os.getpid()
                os.system(f'taskkill /pid {meu_pid} /F')
            sleep(1)

    def registrando(self, txt, color='BLACK', vida='DIA'):
        """Tratativa dos registros gerados manualmente

        Args:
            txt : A mensagem que será enviada ou salva
            vida : Tempo de vida util que o log deve ser mantido
                    'DIA'
                    'SEMANA'
                    'MES'
                    'ANO'
                    'ETERNO'
        """
        ##### * FORMATO EM QUE FICARÁ A MENSAGEM
        registro = str(datetime.now().strftime('%Y/%m/%d-%H:%M:%S-'))+str(txt)
        ##### * ENVIO DA MENSAGEM PARA O FRONT
        self.queue.put([registro,color])
        ##### * SALVA O LOG NO BANCO DE DADOS
        banco.log_grava(txt,vida)
        ##### * SALVA O LOG LOCALMENTE NA MAQUINA
        nome_arquivo_log ='Log_' + Config.ROBOT_NAME.value + str(datetime.now().strftime('%Y%m%d')) + '.txt'
        arquivo_log = open(nome_arquivo_log,'a')
        print (registro, file=arquivo_log)
        arquivo_log.close()

    def apagar_logs(self):
        '''Limpa os arquivos de logs mais antigos'''
        ##### * FAZ LIMPEZA DE LOGS ANTIGOS NO BANCO DE DADOS
        banco.log_apaga()
        ##### * LISTA OS ARQUIVOS DE LOGS EXISTENTES NA PASTA
        list_arquivos_log = glob('Log_' + Config.ROBOT_NAME.value + '*')
        ##### * PARA CADA ARQUIVO FAZ A VERIFICAÇÃO
        for for_arquivo_log in list_arquivos_log:
            data_arquivo = for_arquivo_log.split(Config.ROBOT_NAME.value)[1]
            data_arquivo = datetime.strptime(data_arquivo,'%Y%m%d.txt')
            ##### * SE FOR MAIS ANTIGO QUE OS DIAS ESTIPULADOS, APAGA O ARQUIVO
            if data_arquivo < datetime.now() - timedelta(days=8):
                os.remove(for_arquivo_log)
            else:
                pass   

    def capture(self):
        """Metodo que realiza a caputura de dados de ocorrências já transferidas para a unidade e realiza sua distribuição
        """
        threading.Thread(target=self.check_life).start()            # * VERIFICA A VIDA DA JANELA
        try:                                                        #
            status_window = self.master.state()                     # * MAIS UMA VERIFICAÇÃO DE SEGURANÇA,   
        except:                                                     # * PARA A THREAD NÃO FICAR ABERTA INFINITAMENTE
            status_window = None                                    #
        
        while 'normal' == status_window and self.running == 1:
            ##### * VERIFICA SE ESTÁ NA HORA DA PROXIMA VERIFICAÇÃO
            if(self.nextCapture==None or self.nextCapture.strftime("%d/%m/%Y %H:%M")==datetime.now().strftime("%d/%m/%Y %H:%M")):
                self.registrando                                    ("Iniciando os trabalhos",'BLACK','SEMANA')
                self.apagar_logs()                                  # * APAGA LOGS QUE PERDERAM SUA VIDA ÚTIL
                if self.nextCapture != None:                        # * A CADA PASSADA QUE NÃO FOR A PRIMEIRA VEZ
                    self.make_login(startThread=False)              # * REALIZA RENOVAÇÃO DO LOGIN NO SITE EXEMPLO.COM
                banco.prepare_to_collect()                          # * EXECUTA PROCEDURE
                self.registrando                                    ('Tratando reabertura de ocorrências, por favor, aguarde...','BLACK','SEMANA')
                if banco.check_to_reopen()==False:
                    self.registrando                                ("Ocorreu um erro na procedure: srdist.sp_exemplo_reopen",'RED','ANO')
                self.registrando                                    ('Fechando ocorrências prorrogadas, canceladas ou tratadas','BLACK','SEMANA')
                if banco.close_occurrences()==False:
                    self.registrando                                ("Ocorreu um erro na procedure: sp_exemplo_close_and_adjust",'RED','ANO')
                self.registrando                                    ('Buscando ocorrências para atualizar e distribuir','BLACK','SEMANA')
                ocorrencias = banco.list_occurrences_to_update()    # * LISTA AS OCORRENCIAS DO BANCO DE DADOS
                contRegistry = 1                                    # * PONTO DE MARCAÇÃO DE REGISTROS
                if len(ocorrencias)==0:                             # * VERIFICA A QUANTIDADE DE OCORRENCIAS OBTIDA DO BANCO
                    self.registrando                                ("Não há ocorrências para processar!",'PURPLE','SEMANA')
                    erro = banco.get_last_error()                   # * VERIFICA SE OCORREU ALGUM ERRO NO BANCO DE DADOS
                    if(erro!=None): self.registrando                (erro,'RED','MES')
                else:
                    ##### * ================================================================
                    ##### * INICIO DO TRABALHO DE ATUALIZACAO E DISTRIBUICAO DAS OCORRENCIAS
                    ##### * ================================================================
                    self.registrando                                (f'Há {str(len(ocorrencias))} ocorrências para atualizar e distribuir','GREEN','SEMANA')
                    self.registrando                                ('Preparando ocorrências para iniciar o processo','BLACK','DIA')
                    ##### * REALIZA A TRANSFERENCIA DAS MACROS PARA AS CONDIÇÕES IMPOSTAS PELA CEACRBH
                    ##### * ANTES DE REALIZAR A TRANSFERENCIAS DAS INFORMAÇÕES
                    self.registrando                                ("Preparando ocorrências para coleta",'BLACK','SEMANA')
                    if banco.prepare_to_collect()==False:
                        self.registrando                            ("Ocorreu um erro na procedure: srdist.sp_exemplo_prepare_to_collect",'RED','ANO')
                        self.registrando                            (banco.get_last_error(),'RED','ANO')
                    self.registrando                                ("Fim da preparação de ocorrências para coleta",'BLACK','SEMANA')
                    
                    for num_ocorr in ocorrencias:
                        if contRegistry > 1 and contRegistry%100==0:                            # * RENOVA O LOGIN  CADA 100 OCORRENCIAS
                            self.make_login(startThread=False)
                        ocorrencia = self.site_exemplo.get_occurrence_data(num_ocorr[0])             # * CONSULTA NO SITE O OBTEM OS DADOS DA OCORRENCIA
                        if ocorrencia!=None:                                                    # * SE O RETORNO FOR 'None' É POR QUE HOUVE FALHA DE CONEXAO OU RETORNOU ERRO 500
                            if ocorrencia.com_erro==False:
                                self.registrando                                                ('Atualizou dados da ocorrência '+str(ocorrencia.numOcorrencia),'BLACK','SEMANA')
                                fone_email = str(ocorrencia.telefone)+' '+str(ocorrencia.email) # * NECESSARIO PORQUE O PYTHON ESTAVA SE PERDENDO NA CONCATENACAO DENTRO DO PARAMENTRO
                                if banco.update_info_occurrence(fone_email,ocorrencia.telefone,ocorrencia.email,ocorrencia.manifesto,ocorrencia.numOcorrencia)==False:
                                    self.registrando                                            ("Ocorreu um erro ao tentar atualizar os dados da ocorrencia "+str(ocorrencia.numOcorrencia),'RED','MES')
                                    self.registrando                                            (banco.get_last_error(),'RED','MES')
                            else:
                                ##### * PARA ESSAS OCORRENCIAS QUE TIVERAM ERRO PRECISA ATUALIZAR O STATUS PARA 2 (IGNORADA)
                                ##### * QUANDO HOUVER EXCEPTION NA RESPOSTA DO ERRO
                                ##### * java.util.NoSuchElementException
                                if banco.update_status_occurrence(ocorrencia.numOcorrencia,TransferStatus.IGNORADA)==False:
                                    self.registrando                                            ("Ocorreu um erro ao tentar atualizar o status da ocorrencia "+str(ocorrencia.numOcorrencia),'RED','ANO')
                                    self.registrando                                            (banco.get_last_error(),'RED','ANO') 
                                self.registrando                                                (f'Atualizando status da ocorrencia {str(ocorrencia.numOcorrencia)} por falha','RED','ANO')
                                if banco.remove_occurrence_from_macro(ocorrencia.numOcorrencia)==False:
                                    self.registrando                                            (f"Ocorreu um erro ao tentar excluir a ocorrencia {str(ocorrencia.numOcorrencia)} do processo.",'RED','ANO')
                                    self.registrando                                            (banco.get_last_error(),'RED','ANO')
                                self.registrando                                                ("Ocorreu o seguinte erro: ",'RED','ANO')
                                self.registrando                                                (self.site_exemplo.get_last_error(),'RED','ANO')
                                banco.save_last_error(self.site_exemplo.get_last_error())
                        else:
                            self.registrando                                                    (f"Ocorrência {str(num_ocorr[0])} ignorada por falha na consulta.",'RED','ANO')
                            self.registrando                                                    (self.site_exemplo.get_last_error(),'RED','ANO')
                            banco.save_last_error(self.site_exemplo.get_last_error())
                        contRegistry += 1                                                       # * INCREMENTA O CONTADOR DE REGISTROS
                        sleep(1)

                    self.registrando                                ('Realizando distribuição das ocorrências','ORANGE','SEMANA')
                    total = banco.distribute_occurrences()          # * DISTRIBUI AS OCORRENCIAS
                    if int(total) == 0:
                        self.registrando                            ('Nenhuma ocorrência distribuída','PURPLE','MES')
                    else:
                        self.registrando                            (f'Foram distribuídas {str(total)} ocorrências!','GREEN','MES')
                    self.registrando                                ('Formatando unidade das ocorrências distribuídas.','BLACK','SEMANA')
                    if banco.update_unit()==False:                  # * REALIZA A ATUALIZACAO NA FORMATACAO DAS UNIDADES (ZEROS A ESQUERDA)
                        self.registrando                            ("Ocorreu um erro ao tentar atualizar as unidades das ocorrencias.",'RED','ANO')
                        self.registrando                            (banco.get_last_error(),'RED','ANO')
                    self.registrando                                ('Atualizando subsídios.','BLACK','SEMANA')
                    total = banco.check_subsidy_date()              # * ATUALIZA A DATA DE SUBSIDIO QUANDO HOUVER NECESSIDADE
                    if int(total) == 0:
                        self.registrando                            ('Nenhum subsídio atualizado!','PURPLE','MES')
                    else:
                        self.registrando                            (f"Forma ajustados {str(total)} subsídios",'GREEN','MES')
                    if len(ocorrencias) == int(contRegistry-1):     # * ATUALIZA O INDICADOR DE ATUALIZACAO DAS CAPTURAS
                        if banco.update_macro_log(LogType.LAST_CAPTURE)==False:
                            self.registrando                        ("Ocorreu um erro ao grava o log",'RED','ANO')
                            self.registrando                        (banco.get_last_error(),'RED','ANO')
                try:
                    del ocorrencia
                except:
                    pass
                ##### * =============================================================
                ##### * FIM DO TRABALHO DE ATUALIZACAO E DISTRIBUICAO DAS OCORRENCIAS
                ##### * =============================================================
                try:
                    del ocorrencia
                except:
                    pass
                
                self.transfer()                                     ##### * INVOCA A FUNÇÃO QUE REALIZA TRANSFERENCIAS (((OBS::: FOI USADO COMO "GO TO")))
                ##### * DEIXA DEFINIDO O HORARIO PARA A PROXIMA EXECUÇÃO
                self.nextCapture = datetime.now() + timedelta(minutes=30)
                self.registrando("Próxima execução em: "+self.nextCapture.strftime("%d/%m/%Y %H:%M"),'BLACK','SEMANA')

            sleep(30)                                               # * DORME 30 SEGUNDOS ANTES DO PROXIMO LOOPING
            self.registrando("Próxima execução em: "+self.nextCapture.strftime("%d/%m/%Y %H:%M"),'DIA','SEMANA')
            
            try:                                                    #
                status_window = self.master.state()                 # * MAIS UMA VERIFICAÇÃO DE SEGURANÇA,   
            except:                                                 # * PARA A THREAD NÃO FICAR ABERTA INFINITAMENTE
                status_window = None                                #

    def transfer(self):
        """Metodo responsável por realizar as transferências de ocorrências para dentro do site exemplo.com
        """
        errorOnTransfer = 0                                         # * Marcador de erros em transferencias
        self.make_login(startThread=False)                          # * REALIZA UM NOVO LOGIN NO EXEMPLO.COM PARA GARANTIR A SESSAO
        # * VERIFICA SE ESTA DENTRO DO PERIODO DE EXECUCAO PARA REPROCESSAR OCORRENCIAS NAO TRANSFERIDAS
        if (( datetime.now().time() >= time( 8,0) and datetime.now().time() <= time( 8,30) ) or 
            ( datetime.now().time() >= time(12,0) and datetime.now().time() <= time(12,30) ) or
            ( datetime.now().time() >= time(15,0) and datetime.now().time() <= time(15,30) ) or
            ( datetime.now().time() >= time(17,0) and datetime.now().time() <= time(17,30) ) or
            ( datetime.now().time() >= time(19,0) and datetime.now().time() <= time(19,30) )):
            if banco.check_occurrences_not_transfered()==False:
                self.registrando                                    ("Ocorreu um erro ao tentar tratar as ocorrencias não transferidas.",'RED','ANO')
                self.registrando                                    (banco.get_last_error(),'RED','ANO')
            else:
                self.registrando                                    ("Verificando ocorrências que não foram transferidas",'BLACK','SEMANA')
        self.registrando                                            ("Definindo se há ocorrências para transferir",'BLACK','SEMANA')
        if banco.set_occurrences_to_transfer()==False:
            self.registrando                                        ("Erro ao definir ocorrências para transferir",'RED','ANO')
            self.registrando                                        (banco.get_last_error(),'RED','ANO')
        else:
            ocorrencias = banco.list_occrurences_to_transfer()      # * OBTEM AS OCORRENCIAS QUE SERAO TRANSFERIDAS
            contRegistry = 1                                        # * CONTADOR DE REGISTROS
            if len(ocorrencias) == 0:
                self.registrando                                    ("Não há ocorrências para transferir!",'PURPLE','MES')
            else:
                self.registrando                                    (f'Há {str(len(ocorrencias))} ocorrências para transferir','GREEN','MES')

                for ocor in ocorrencias:
                    ocorrencia = self.site_exemplo.get_occurrence_data(ocor[0])                      # * CONSULTA A OCORRENCIA ANTES DE TRANSFERIR
                    if ocorrencia!=None:                                                        # * VERIFICA SE ENCONTROU A OCORRENCIA
                        if ocorrencia.situacao=="Enviada":                                      # * VERIFICA A SITUACAO DA OCORRENCIA
                            ##### * PREENCHE O RESTANTE DOS DADOS DA OCORRENCIA ANTES DE TRANSFERIR
                            ocorrencia.dataSolucaoUltimaMov = self.site_exemplo.get_date_last_mov(ocor[0])
                            ocorrencia.numOcorrencia        = ocor[0]
                            ocorrencia.numeroUnidadeUsuario = ocor[2]
                            ocorrencia.numeroNaturalUsuario = ocor[3]
                            ocorrencia.numUnidadeAtual      = ocor[6]
                            ocorrencia.numNaturalAtual      = ocor[5]
                            ocorrencia.mascaraUnidadeAtual  = ocor[4]
                            ocorrencia.unidDestFormat       = ocor[7]
                            ocorrencia.numUnidadeDestino    = ocor[8]
                            ocorrencia.numNaturalDestino    = ocor[5]
                            ocorrencia.mascaraUnidadeDestino= ocor[6]
                            ocorrencia.emailUnidadeUsuario  = ocor[9]
                            
                            if self.site_exemplo.transfer_occurrence(ocorrencia)==True:              # * TENTA REALIZAR A TRANSFERENCIA DA OCORRENCIA
                                self.registrando                                                (f'Transferiu a ocorrência {str(ocorrencia.numOcorrencia)}','BLACK','SEMANA')
                                if banco.update_status_occurrence(ocorrencia.numOcorrencia,TransferStatus.TRANSFERIDA)==False:
                                    self.registrando                                            (f"Ocorreu um erro ao tentar atualizar o status de transferencia da ocorrencia {str(ocorrencia.numOcorrencia)}",'RED','ANO')
                                    self.registrando                                            (banco.get_last_error(),'RED','ANO')
                            else:
                                self.registrando                                                (f"Erro ao realizar transferência da ocorrência {str(ocorrencia.numOcorrencia)}",'RED','ANO')
                                self.registrando                                                (self.site_exemplo.get_last_error(),'RED','ANO')
                                banco.save_last_error(self.site_exemplo.get_last_error())
                                errorOnTransfer += 1
                            contRegistry += 1                                                   # * INCREMENTA O CONTADOR DE REGISTROS
                            sleep(1)
                        else:
                            self.registrando                                                    (f"Ocorrência {str(ocor[0])} já respondida então não será transferida!",'BLACK','SEMANA')
                            banco.update_status_occurrence(ocor[0],TransferStatus.RESPONDIDA)
                        del ocorrencia                                                          # * EXCLUI O OBJETO E LIBERA A MEMORIA SOH SE EXISTIR
                    else:
                        self.registrando                                                        (f"Erro ao consultar ocorrência {str(ocor[0])} para transferir",'RED','ANO')
                        self.registrando                                                        (self.site_exemplo.get_last_error(),'RED','ANO')
                        banco.save_last_error(self.site_exemplo.get_last_error())
                
                if len(ocorrencias) == int(contRegistry-1):         # * ATUALIZA O INDICADOR DE ATUALIZACAO DAS CAPTURAS
                    if banco.update_macro_log(LogType.LAST_TRANSFER)==False:
                        self.registrando                            ("Ocorreu um erro ao gravar o log",'RED','ANO')
                        self.registrando                            (banco.get_last_error(),'RED','ANO')
                if errorOnTransfer == 0:
                    self.registrando                                (f"Foram transferidas {str(len(ocorrencias))} com sucesso!",'GREEN','MES')
                else:
                    self.registrando                                (f"Foram transferidas {str(len(ocorrencias)-errorOnTransfer)} com sucesso!",'GREEN','MES')
                    self.registrando                                (f"Foram transferidas {str(errorOnTransfer)} com falha!",'INDIGO','MES')
            
            if banco.update_macro_log(LogType.LAST_EXECUTION)==False:
                self.registrando                                    ("Ocorreu um erro ao grava o log",'RED','ANO')
                self.registrando                                    (banco.get_last_error(),'RED','ANO')

            try:
                del ocorrencias
            except:
                pass



##### * INICIALIZAÇÃO DO FRONT
root = tkinter.Tk()                                                 # * CRIAÇÃO DA JANELA PRINCIPAL
icone = resource_filename(__name__, 'favicon.ico')                  # * PREPARA UM ICONE
root.iconbitmap(icone)                                              # * DEFINE O ICONE NA JANELA
root.title(f'{Config.ROBOT_NAME.value}{Config.VERSION.value}')      # * CONFIGURA O TITULO DA JANELA
root.resizable(True,True)                                           # * PERMITE QUE A JANELA SEJA REDIMENSIONADA
root.geometry("670x450")                                            # * DEFINE O TAMANHO DA INICIAL DA JANELA
app = Application(root)                                             # * PASSA A JANELA PRINCIPAL ATRAVÉS DA CLASSE PRINCIPAL
app.make_login()                                                    # * INVOCA A FUNÇÃO INICIAL COM A PRINCIPAL ROTINA
root.mainloop()                                                     # * REALIZA A ABERTURA DA JANELA PRINCIPAL