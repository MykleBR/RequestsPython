from cryptography.fernet import Fernet
import pyodbc
from config import Config

######################################################
##### APRESENTAÇÃO
print ('\n\n')
print ('BEM VINDO')
print ('Este é o gerenciador de senhas de gestores')
print ('Versão do gerenciador de senha: 1.0')
print ('\n\n')
######################################################

######################################################
##### OBTENDO AS INFORMAÇÕES DO USUÁRIO
matricula = input('Digite a "MATRICULA" do gestor que deseja enviar ao "Banco de Dados", e pressione "Enter"\n')
senha_pura = input('Digite a "SENHA" do gestor que deseja enviar ao "Banco de Dados", e pressione "Enter"\n')
print ('\nAtualizando "Banco de Dados"...\n')
######################################################

######################################################
##### SISTEMA DE CRYPTO
key = b'N-nMdHttV7-iyB_FxR9Q6NlfkEd1QGp12iVfn-RPEZY='
f = Fernet(key)

def encrypta(senha):
    '''Encriptador de senhas'''
    enc = f.encrypt(senha.encode())
    enc = str(str(enc).replace("b'", "")).replace("'",'')
    return enc

def decrypta(senha):
    '''Descriptografa as senhas'''
    dec = f.decrypt(senha)
    dec = str(str(dec).replace("b'", "")).replace("'",'')
    return dec

senha_cripto = encrypta(senha_pura)
# print (senha_cripto)
# print(decrypta(senha_cripto.encode('ascii')))
######################################################

######################################################
##### GRAVA NO BANCO DE DADOS
conex = pyodbc.connect('DRIVER={SQL Server};'
                'SERVER='+str(Config.DB_HOST.value)+';'
                'DATABASE='+str(Config.DB_NAME.value)+';'
                'UID='+str(Config.DB_USER.value)+';'
                'PWD='+str(Config.DB_PASS.value),
                autocommit=True)

try:
    sql=f"""
    DELETE FROM srdist.tb_gestor
    WHERE [username] = '{matricula}'  
    
    INSERT INTO srdist.tb_gestor
    ([username],[password],[dt_insert])
    VALUES
    ('{matricula}','{senha_cripto}',GETDATE())
    """
    cur = conex.cursor()
    cur.execute(sql)
    cur.close()
    print ('Informações atualizadas no "Banco de Dados" com sucesso!')
except:
    print ('OCORREU ALGUM ERRO AO TENTAR ATUALIZAR O BANCO DE DADOS')
    print ('Tente novamente mais tarde...')
######################################################

######################################################
print ('\nEste programa já pode ser finalizado!')
######################################################

finaliza = input('Pressione "ENTER" para sair\n')