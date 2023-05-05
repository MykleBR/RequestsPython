from enum import Enum
from cryptography.fernet import Fernet

class Sensiveis (Enum):
    """Classe para proteger informações com dados sensiveis"""
    DB_PASS     = ""
    DBROB_PASS  = ""

    def decrypta(senha):
        ''' # Descriptografa as senhas'''
        key = b'N-nMdHttV7-iyB_FxR9Q6NlfkEd1QGp12iVfn-RPEZY='
        f = Fernet(key)    
        dec = f.decrypt(senha)
        dec = str(str(dec).replace("b'", "")).replace("'",'')
        return dec

class Config(Enum):
    """ * Configurações básicas do robô"""
    VERSION             = ''
    ROBOT_NAME          = ''             # NOME DO ROBÔ
    
    DB_HOST             = ''
    DB_NAME             = ''
    DB_USER             = ''
    DB_PASS             = Sensiveis.decrypta(Sensiveis.DB_PASS.value.encode('ascii')) 

    DBROB_HOST          = ''
    DBROB_NAME          = ''
    DBROB_USER          = ''
    DBROB_PASS          = Sensiveis.decrypta(Sensiveis.DBROB_PASS.value.encode('ascii'))

class LogType(Enum):
    """Enumerador para diferenciar os tipos de logs do sistema

    Attributes:
        LAST_TRANSFER (int): Execução da última vez que realizou a transferência
        LAST_CAPTURE (int): Execução da última vez que realizou uma captura
        LAST_EXECUTION (int): Última vez que o robô foi executando tendo feito um, ambos ou nenhum procedimento
    """
    LAST_TRANSFER       = 1
    LAST_CAPTURE        = 2
    LAST_EXECUTION      = 3

class TransferStatus(Enum):
    """Enumerador para diferenciar os tipos de transferências executadas pelo sistema

    Attributes:
        TRANSFERIDA (int): Define se uma ocorrência foi transferia
        IGNORADA (int): Caso a ocorrência tenha falhado em sua consulta, ela é marcada como ignorada
        RESPONDIDA (int): Se uma ocorrência já estiver como respondida, então desmarca a opção de transferí-la
    """
    TRANSFERIDA         = 1
    IGNORADA            = 2
    RESPONDIDA          = 3

