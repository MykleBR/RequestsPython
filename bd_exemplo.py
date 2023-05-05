from config import Config,TransferStatus,LogType
import pyodbc
import os

class BdExemplo:
    conn = None
    lastError = None
    def __init__(self):

        self.connRobo =     pyodbc.connect('DRIVER={SQL Server};'
                            'SERVER='+str(Config.DBROB_HOST.value)+';'
                            'DATABASE='+str(Config.DBROB_NAME.value)+';'
                            'UID='+str(Config.DBROB_USER.value)+';'
                            'PWD='+str(Config.DBROB_PASS.value),
                            autocommit=True
                            )

        #realiza a conexao atraves do BD Suporte
        self.conn =         pyodbc.connect('DRIVER={SQL Server};'
                            'SERVER='+str(Config.DB_HOST.value)+';'
                            'DATABASE='+str(Config.DB_NAME.value)+';'
                            'UID='+str(Config.DB_USER.value)+';'
                            'PWD='+str(Config.DB_PASS.value),
                            autocommit=True
                            )
    
    def save_last_error(self,error:str):
        import socket
        maq = socket.gethostname()
        usr = os.getlogin()

        cur = self.connRobo.cursor()
        sql = "INSERT INTO erros(DH_ACAO,IC_APLICACAO,NO_MAQUINA,CO_USUARIO,DE_ERRO) "
        sql+= "VALUES(GETDATE(),'"+Config.ROBOT_NAME.value+"','"+str(maq)+"','"+str(usr)+"','"+str(error)+"')"
        cur.execute(sql)
        cur.close()

    def disconnect(self):
        self.conn.close()
        self.connRobo.close()

    def get_last_error(self):
        return self.lastError

    def check_logged(self):
        """Metodo que verifica se jah ha um usuario logado utilizando o sistema

        Args:
            username (string): matricula do usuario

        Returns:
            Any: False or Database Object
        """
        retorno = False
        try:
            cur = self.connRobo.cursor()
            cur.execute("SELECT DH_LOGIN,CO_USUARIO FROM atividade WHERE IC_APLICACAO='"+Config.ROBOT_NAME.value+"'")
            #cur.execute("SELECT data_hora,username FROM srdist.tb_robo_logado WHERE tipo='"+Config.ROBOT_NAME.value+"'")
            res = cur.fetchone()
            if res!=None:
                retorno = res
        except pyodbc.Error as e:
            self.lastError = format(e)
            retorno = False
            pass
        
        return retorno

    def save_logged(self):
        """Metodo que salva o login de um usuario no sistema para futura verificacao

        Returns:
            Boolean: True ou False
        """
        username = os.getlogin()
        retorno = False
        try:
            cur = self.connRobo.cursor()
            cur.execute("INSERT INTO atividade(DH_LOGIN,CO_USUARIO,IC_APLICACAO) VALUES(GETDATE(),'"+str(username)+"','"+Config.ROBOT_NAME.value+"')")
            #cur.execute("INSERT INTO srdist.tb_robo_logado(data_hora,username,tipo) VALUES(GETDATE(),'"+str(username)+"','"+Config.ROBOT_NAME.value+"')")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            pass

        return retorno

    def update_status_logged(self):
        """Metodo que atualiza a cada 5 minutos se o robo estah executando

        Returns:
            Boolean: True ou False
        """
        retorno = False
        username = os.getlogin()
        try:
            cur = self.connRobo.cursor()
            cur.execute("UPDATE atividade SET DH_STATUS=GETDATE() WHERE IC_APLICACAO='"+Config.ROBOT_NAME.value+"'"+"AND CO_USUARIO = '"+username+"'")
            #cur.execute("UPDATE BD_SUPORTE.srdist.tb_robo_logado SET check_login=GETDATE() WHERE tipo='"+Config.ROBOT_NAME.value+"'")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            pass

        return retorno
		
    def del_logged(self):
        """Metodo que libera a tabela de usuarios logados

        Returns:
            Boolean: True ou False
        """
        username = os.getlogin()
        retorno = False
        try:
            cur = self.connRobo.cursor()
            cur.execute("DELETE atividade WHERE IC_APLICACAO='"+Config.ROBOT_NAME.value+"' AND CO_USUARIO='"+str(username)+"'")
            #cur.execute("DELETE FROM srdist.tb_robo_logado WHERE tipo='"+Config.ROBOT_NAME.value+"'")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            pass
        
        return retorno

    def log_grava(self,msg_log,vida):
        '''Verifica execução do robô salva no banco de dados'''
        retorno = False
        usuario = os.getlogin()
        try:
            cur = self.connRobo.cursor()
            sql = f"""  
            INSERT INTO [dbo].[b003_logs]
            ([DH_INSERT]
            ,[NOME_ROBO]
            ,[USUARIO]
            ,[LOG]
            ,[VIDA])
            VALUES
            (GETDATE(),
            '{Config.ROBOT_NAME.value}',
            '{usuario}',
            '{msg_log}',
            '{vida}')                
            """
            cur.execute(sql)
            retorno = True
        except pyodbc.Error as e:
            lastError = format(e)
            retorno = lastError
        return retorno

    def log_apaga(self):
        '''Apaga os logs antigos do banco de dados'''
        retorno = False
        try:
            cur = self.connRobo.cursor()
            sql = f"""  
            DELETE
            FROM [dbo].[b003_logs] 
            WHERE	VIDA = 'DIA'		AND DH_INSERT < DATEADD(DAY,	-1 ,GETDATE())
            OR		VIDA = 'SEMANA'		AND DH_INSERT < DATEADD(WEEK,	-1 ,GETDATE())
            OR		VIDA = 'MES'		AND DH_INSERT < DATEADD(MONTH,	-1 ,GETDATE())
            OR		VIDA = 'ANO'		AND DH_INSERT < DATEADD(YEAR,	-1 ,GETDATE())    
            """
            cur.execute(sql)
            retorno = True
        except pyodbc.Error as e:
            lastError = format(e)
            retorno = lastError
        return retorno    

    def get_gestor(self):
        """Método que seleciona o usuário e senha que será utilizado para logar no exemplo.com"""
        res = None
        try:
            cur = self.conn.cursor()
            sql = """
            SELECT TOP (1) [username],[password]
            FROM [SUPORTE].[dist].[tb_gestor]
            WHERE dt_invalid is null
            ORDER BY  dt_insert ASC
                    """
            cur.execute(sql)
            res = cur.fetchone()
            cur.close()
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
        return res        

    def invalid_gestor(self,gestor):
        """Define a senha do gestor para inválida no banco de dados"""
        res = False
        try:
            cur = self.conn.cursor()
            sql = f"""
            UPDATE [SUPORTE].[dist].[tb_gestor]
            SET [dt_invalid] = GETDATE()
            WHERE [username] = '{gestor}'            
            """
            cur.execute(sql)
            cur.close()
            res = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
        return res        

    def check_to_reopen(self):
        """Metodo que chama a procedure que realizar a reabertura das ocorrencias quando necessario

        Returns:
            Boolean: True ou False
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_reopen")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno

    def close_occurrences(self):
        """Metodo finaliza no exemplo as ocorrencias prorrogadas, canceladas ou prorrogadas que ja foram tratadas

        Returns:
            Boolean: True ou False
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_close_and_adjust")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
        
        return retorno

    def check_occurrences_not_transfered(self):
        """Metodo que verifica as transferencias que NAO foram transferidas nos ultimos 15 dias

        Returns:
            None: Nada
        """
        retorno = False
        try:
            cur =self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_verify_oc_transfered")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno

    def set_occurrences_to_transfer(self):
        """Metodo que define quais serao as ocorrencias que deverao ser trasferidas

        Returns:
            None: Nada
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_transfer_oc")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno

    def prepare_to_collect(self):
        """Metodo que realiza a migracao para a SUPORTE.tabela tb_ocorrencia_macro 
           das ocorrencias que serao transferidas

        Returns:
            boolean: Verdadeiro ou falso
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("exec srdist.sp_exemplo_prepare_to_collect")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno

    def list_occrurences_to_transfer(self):
        """Metodo que lista os codigos das ocorrencias que teraoh os dados atualizados

        Returns:
            Array: Array contendo os numeros das ocorrencias
        """
        res = None
        try:
            cur = self.conn.cursor()
            sql = """SELECT 
            nu_ocorrencia,
            FORMAT(dt_vencimento,'dd/MM/yyyy') as vencimento,
            nu_unidade_usuario,
            (SELECT numero_natural_usuario FROM ENTRADA.dist.tb_exemplo WHERE cgc=nu_unidade_usuario) as nu_natural_usuario,
            nu_unidade_envolvida,
            (SELECT numero_natural_usuario FROM ENTRADA.dist.tb_exemplo WHERE cgc=nu_unidade_usuario) as nu_natural_atual,
            (SELECT sigla FROM ENTRADA.dist.tb_exemplo WHERE cgc=nu_unidade_usuario) as masc_unidade_atual,
            (SELECT sigla FROM ENTRADA.dist.tb_exemplo WHERE cgc=nu_unidade_usuario) as un_dest_format,
            nu_unidade_destino,
            (SELECT email_unidade_usuario FROM ENTRADA.dist.tb_exemplo WHERE cgc=nu_unidade_usuario) as em_unidade_usuario
            FROM BD_ENTRADA.srdist.tb_ocorrencia_transferir
            WHERE status_oc IS NULL and nu_ocorrencia NOT IN( SELECT NU_OCORRENCIA FROM PR001330.SUPORTE.TB_OCORRENCIA OC
            INNER REMOTE JOIN PR001330.SUPORTE.TB_ITEM IT ON OC.NU_ITEM=IT.NU_ITEM
            INNER REMOTE JOIN PR001330.SUPORTE.TB_ASSUNTO SUB ON IT.NU_ASSUNTO=SUB.NU_ASSUNTO
            WHERE cast(OC.dh_ocorrencia as date) >= cast(getdate()-90 as date)
            AND OC.NU_NATUREZA = 5
            AND OC.NU_ITEM = 9469
            AND OC.NU_MOTIVO = 14538
            AND SUB.NU_ASSUNTO = 7
            AND OC.NU_UNIDADE_DESTINO NOT IN(7391))
            """
            cur.execute(sql)
            res = cur.fetchall()
            cur.close()
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return res

    def list_occurrences_to_update(self):
        """Metodo que lista as ocorrencias que estao na tabela da macro e que nao foram atualizadas

        Returns:
            Array: Numeros das ocorrencias
        """
        res = None
        try:
            cur = self.conn.cursor()
            cur.execute("select nu_ocorrencia FROM ENTRADA.tb_ocorrencia_macro WHERE manifesto IS NULL OR manifesto=''")
            res = cur.fetchall()
            cur.close()
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return res

    def update_info_occurrence(self,fone_mail:str,fone:str,email:str,manifesto:str,ocorrencia:str):
        """Metodo que realiza a atualizacao das informacoes de uma determinada ocorrencia

        Args:
            fone_mail (string): Telefone concatenado com o e-mail do manifestante
            manifesto (string): Texto do manifesto
            ocorrencia (string): Codigo da ocorrencia

        Returns:
            Boolean: True ou False
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE ENTRADA.tb_ocorrencia_macro SET telefone_email = '"+str(fone_mail)+"',telefone='"+str(fone)+"',e_mail='"+str(email)+"',manifesto ='"+str(manifesto)+"' WHERE nu_ocorrencia ="+str(ocorrencia))
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
            
        return retorno

    def update_status_occurrence(self,ocorrencia:str,status:TransferStatus):
        """Metodo que realiza atualizacao do status da ocorrencia na tabela tb_ocorrencia_macro.
        Args:
            ocorrencia (int): Codigo da ocorrencia que terah seu status alterado
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("UPDATE ENTRADA.tb_ocorrencia_transferir SET status_oc='"+str(status.value)+"',dt_transferencia=getdate() WHERE nu_ocorrencia="+str(ocorrencia))
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno
    
    def remove_occurrence_from_macro(self,ocorrencia:str):
        """Metodo que remove uma ocorrencia com falha da tabela de ocorrencias para tratamento

        Args:
            ocorrencia (int): Codigo da Ocorrencia

        Returns:
            Boolean: True or False
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM SUPORTE.tb_ocorrencia_macro WHERE nu_ocorrencia="+str(ocorrencia))
            cur.close()
            #print("Atualizado com sucesso")
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno
       
    def distribute_occurrences(self):
        """Metodo que realiza a distribuicao das uma ocorrencia dentro do portal

        Returns:
            int : Total de registros movidos para o exemplo
        """
        retorno = 0
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_move_to_mask")
            retorno = cur.fetchval()
            #atualiza a atualizacao da rotina para acompanhamento no portal
            #self.update_macro_log(3)
            cur.close()
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass


        return retorno
    
    def update_unit(self):
        """Metodo que realiza a atualizacao da unidade das ocorrencias na mascara
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_update_mask_unity")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass

        return retorno

    def check_subsidy_date(self):
        """Metodo que verifica e atualiza a data de subsidio das ocorrencias

        Returns:
            int : Numero de ocorrencias que tiveram atualizacao no subsidio
        """
        retorno = 0
        try:
            cur = self.conn.cursor()
            cur.execute("EXEC srdist.sp_exemplo_check_subsidy_date")
            retorno = cur.fetchval()
            cur.close()
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
        return retorno

    def update_macro_log(self,logType:LogType):
        """Metodo que realiza a atualizacao das informacoes para exibir no resumo de tela do exemplo

        Args:
            logType (int): 
                        1 = Ultima transferencia realizada\n
                        2 = Ultima captura dos dados\n
                        3 = Ultima execucao do robo\n
        """
        retorno = False
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO tb_rotina_macro(dt_rotina_macro,id_macro_fk) VALUES(GETDATE(),"+str(logType.value)+")")
            cur.close()
            retorno = True
        except pyodbc.Error as e:
            self.lastError = format(e)
            self.save_last_error(self.lastError)
            pass
        return retorno
