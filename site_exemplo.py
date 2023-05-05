import requests
import urllib3
from datetime import datetime

class Ocorrencia:
    """Classe de entidade para formatacao das informacoes de uma ocorrencia
    """
    def __init__(self):
        #dados para complementar a distribuicao
        self.telefone               = None
        self.email                  = None
        self.manifesto              = None
        self.situacao               = None
        self.com_erro               = False

        #dados necessarios para transferencia
        self.dataSolucaoUltimaMov   = None
        self.numOcorrencia          = None
        self.numeroUnidadeUsuario   = None
        self.numeroNaturalUsuario   = None
        self.numUnidadeAtual        = None
        self.numNaturalAtual        = None
        self.mascaraUnidadeAtual    = None
        self.unidDestFormat         = None
        self.numUnidadeDestino      = None
        self.numNaturalDestino      = None
        self.mascaraUnidadeDestino  = None
        self.emailUnidadeUsuario    = None

        #dados que podem ser necessarios em caso de fechamento
        self.nom_solicita           = None
        self.cpf_solicita           = None
        self.comentario             = None
        self.data_resposta          = None
        

class Exemplo:
    """Classe que realiza o tratamento de acesso ao site do exemplo.com. 
    Dentre as funcionalidade disponíveis nessa classe estão:
    1. Consulta de ocorrência
    2. Transferência de ocorrência
    3. Fechamento de ocorrência
    4. Abertura de ocorrência (não desenvolvido)
    5. Realização de login no site pa

    Returns:
        [type]: [description]
    """
    nav         = None
    lastError   = None
    def __init__(self):
        #remove o warning de excessao da verificacao do certificado SSL
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        #inicia a sessao do request
        self.nav = requests.Session()
        #define que nao irah verirficar o SSL
        self.nav.verify = False
        #finge que é um navegador
        self.nav.headers = {"User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:81.0) Gecko/20100101 Firefox/81.0"}

    def make_login(self,username:str,password:str):
        """Metodo que realiza login no site do exemplo.com

        Args:
            username (str): login do funcionario (matricula do AD)
            password (str): senha de acesso (senha do AD)

        Returns:
            int: Se houve erro no site: -1
                 Se houve falha de login: 0
                 Se houve sucesso: 1
        """
        retorno = -1
        params  = {"j_username":username,"j_password":password}

        #tenta realizar acesso no exemplo.com
        try:
            respLogin = self.nav.post("https://exemplo.com/login",params=params)
            if(respLogin.status_code==200):
                #verifica se houve mensagem de login ou senha invalidos
                if(respLogin.text.find("Recurso não encontrado: Usuário ou Senha inválido. ")> -1 ):
                    retorno = 0
                else:
                    retorno = 1
            else:
                retorno = -1
        except Exception as e:
            self.lastError = format(e)
            pass

        return retorno

    def get_date_last_mov(self,numOcorrencia:str):
        """ Pega a data da solução da ultima movimentação"""
        retorno = None
        try:
            respCons = self.nav.post("https://exemplo.com/TransferirOcorrencia.do?method=iniciarTransferencia&ocorrencia="+str(numOcorrencia)+"&tipoOcorrencia=3&fase=2")
            if respCons.status_code==200:
                lines = respCons.text.splitlines()
                for index,elem in enumerate(lines):
                    if(index+1 <len(lines) and index -1 >= 0):
                        if (elem.find("<input type=\"hidden\" name=\"dataSolucaoUltimaMov\" value=\"") > -1):
                            return elem.replace("<input type=\"hidden\" name=\"dataSolucaoUltimaMov\" value=\"","").replace("\"/>","")
                return None
        except Exception as e:
            self.lastError = format(e)
            pass
            
        return retorno

    def get_occurrence_data(self,numOcorrencia:str):
        """Metodo que busca as informacoes complementares de uma ocorrencia que sao:
           Telefone,
           E-mail,
           Manifesto,
           Situação,
           Condição de erro,

        Args:
            ocorrencia (int): Número da ocorrência

        Returns:
            Any: Objeto ocorrência ou None
        """
        retorno = None
        paramOcorrencia = {
            "method"                            :"iniciarDetalhamento",
            # "method"                          :"consultarPreOcorrencia",
            "unidadeRemetente"                  :"2",
            "tipoOcorrenciaClassificacao"       :"",
            "situacaoClassificacao"             :"",
            "assuntoClassificacao"              :"",
            "itemClassificacao"                 :"",
            "motivoClassificacao"               :"",
            "guardaTextoUnidadeDestino"         :"",
            "operador"                          :"",
            "perfilUsuario"                     :"administrador",
            "escopo"                            :"I",
            "gravaHistorico"                    :"S",
            "coUnidadePesquisa"                 :"",
            "ordenacaoOuvidoria"                :"1",
            "ordenacaoSac"                      :"1",
            "ordenacaoInterna"                  :"1",
            "tipoOrdenacaoOuvidoria"            :"ASC",
            "tipoOrdenacaoSac"                  :"ASC",
            "tipoOrdenacaoInterna"              :"ASC",
            "sequencialTipoConsulta"            :"1",
            "sequencialTipoOcorrenciaInterna"   :"1",
            "cpf"                               :"",
            "cnpj"                              :"",
            "nis"                               :"",
            "usuarioSolicitante"                :"",
            "sequencialOcorrencia"              :numOcorrencia, #numero da ocorrencia que serah consultada
            "sequencialPreOcorrencia"           :"",
            "nuProtSac"                         :"",
            "anoRar"                            :"",
            "numeroRar"                         :"",
            "ufRar"                             :"-1",
            "periodoInicial"                    :"",
            "periodoFinal"                      :""
        }

        try:
            #realiza chamada na pagina de detalhes da ocorrencia
            respCons = self.nav.post("https://exemplo.com/DetalharOcorrencia.do",params=paramOcorrencia)
            # print(self.nav)
            # print(respCons.encoding)
            if respCons.status_code==200:
                #cria um array de retorno
                retorno = Ocorrencia()
                #define o numero da ocorrencia no objeto
                retorno.numOcorrencia = numOcorrencia

                lines = respCons.text.splitlines()
                #varre cada linha do retorno que foi convertido em array
                for index,elem in enumerate(lines):
                    if(index+1 <len(lines) and index -1 >= 0):
                        #verifica se encontrou a descricao do telefone
                        if (elem.find("<b>&nbsp;Telefone</b>") > -1):
                            #remove __ e espacos a direita e esquerda
                            retorno.telefone = str(lines[index+1]).replace("#","").replace("\"","").replace("'","").replace("&nbsp;","").replace("__","").strip()
                            
                        #verifica se encontrou a descricao de correio
                        if (elem.find("<b>&nbsp;Correio Eletrônico</b>") > -1):
                            #remove espacos em html, espachos em branco a direta e esquerda e converte para minusculo
                            retorno.email = str(lines[index+1]).replace("&nbsp;","").replace("#","").replace("\"","").replace("'","").strip().lower()
                        
                        #verifica se encontoru o manifesto
                        if (elem.find("<b>&nbsp;Manifesto</b>") > -1):
                            #aqui "salva" o manifesto que fica na quarta linha apos a descricao
                            retorno.manifesto = str(lines[index+4]).replace("#","").replace("\"","").replace("'","")

                        #verifica se a ocorrencia jah estah encerrada
                        if (elem.find("<b>Situação</b>&nbsp;") > -1):
                            retorno.situacao = lines[index+2].strip()

                        #verifica se encontrou o solicitante da ocorrencia
                        if elem.find("<b>Solicitante</b>") > -1:
                            linha_solicitante = lines[index+2].split(' - ')
                            retorno.cpf_solicita = linha_solicitante[0].replace("</a>","").replace("<a href=\"javascript: abrirPopUp('DetalharOcorrencia.do?method=iniciarAlterarSolicitante&' + queryString, 650, 500, false);\">","").strip()
                            retorno.nom_solicita = linha_solicitante[1].replace("</a>","").replace("<a href=\"javascript: abrirPopUp('DetalharOcorrencia.do?method=iniciarAlterarSolicitante&' + queryString, 650, 500, false);\">","").strip()
                        
                        #busca o comentario da ocorrencia
                        if elem.find("<b>&nbsp;Comentário</b>") > -1:
                            comentario = str(lines[index+4])
                            retorno.comentario = comentario.replace("#","").replace("\"","").replace("'","")

                        #verifica se encontrou a data da ultima resposta
                        if elem.find("<b>&nbsp;Data Resposta</b>") > -1:
                            retorno.data_resposta = str(lines[index]).replace("<td colspan = \"2\" ><b>&nbsp;Data Resposta</b>&nbsp;","").strip()

                        if (elem.find("<span class=\"fontetitulotela\">Erro</span>") > -1):
                            #para essas ocorrencias que tiveram erro precisa atualizar o status para 2
                            #quando houver exception na resposta do erro
                            #java.util.NoSuchElementException
                            retorno.com_erro = True
        except Exception as e:
            self.lastError = format(e)
            pass

        return retorno

    def transfer_occurrence(self,ocorrencia:Ocorrencia):
        """Metodo que realiza a transferencia de unidade de uma ocorrencia

        Args:
            ocorrencia (Ocorrencia): Objeto com os dados para realizar a transferência

        Returns:
            Boolean: True ou False
        """
        paramTransf = {
            "situacaoUltimaMov"         : "2",
            "dataSolucaoUltimaMov"      : ocorrencia.dataSolucaoUltimaMov,
            "dataSolucaoUltM"           : "",
            "prazoSolucaoUltimaMov"     : "0",
            "coUnidadePesquisa"         : "",
            "coUnidadePesquisa"         : "",
            "ocorrencia"                : ocorrencia.numOcorrencia, #numero da ocorrencia
            "tipoOcorrencia"            : "3",
            "fase"                      : "2",
            "verificaPendecia"          : "0",
            "manifesto"                 : "",
            "numeroUnidadeUsuario"      : ocorrencia.numeroUnidadeUsuario,
            "numeroNaturalUsuario"      : ocorrencia.numeroNaturalUsuario,
            "numUnidadeAtual"           : ocorrencia.numUnidadeAtual,
            "sgUnidadeAtual"            : "CERAT",
            "numNaturalAtual"           : ocorrencia.numNaturalAtual,
            "mascaraUnidadeAtual"       : ocorrencia.mascaraUnidadeAtual,
            "unidDestFormat"            : ocorrencia.unidDestFormat,
            "codigoUniDestino"          : "",
            "numUnidadeDestino"         : ocorrencia.numUnidadeDestino,
            "sgUnidadeDestino"          : "CERAT",
            "numNaturalDestino"         : ocorrencia.numNaturalDestino,
            "mascaraUnidadeDestino"     : ocorrencia.mascaraUnidadeDestino,
            "justificativa"             : "Ocorr&ecirc;ncia tratada pelo SAC Centralizado...",
            "emailUnidadeUsuario"       : ocorrencia.emailUnidadeUsuario
        }

        try:
            #tenta realizar a transferencia
            respTransf = self.nav.post("https://exemplo.com/TransferirOcorrencia.do?method=efetuarTransferencia",params=paramTransf)
            #se obteve sucesso na resposta retorna true
            if respTransf.status_code==200:
                return True
        except Exception as e:
            self.lastError = format(e)
            pass

        return False

    def close_occurrence(self,ocorrencia:Ocorrencia,matFechamento:str):
        """Metodo que realiza o fechamento de uma ocorrencia

        Args:
            ocorrencia (Ocorrencia): Objeto com os dados para fechamento da ocorrencia
            matFechamento (str): Matricula de quem irah fechar a ocorrencia (deve ser a mesma matricula de login)

        Returns:
            Boolean: True ou False
        """
        parClose = {
            "exibeAceite"                   :"N",
            "dataSolucaoUltimaMov"          :ocorrencia.data_resposta,
            "prazoSolucaoUltimaMov"         :"0",
            "numUnidadeUltimaMov"           :"7399",
            "numNaturalUltimaMov"           :"6621",
            "numUnidadeDestinoUltimaMov"    :"7391",
            "numNaturalDestinoUltimaMov"    :"6618",
            "anonimo"                       :"N",
            "origem"                        :"",
            "cpfSolicitante"                :ocorrencia.cpf_solicita,
            "nomeSolicitante"               :ocorrencia.nom_solicita,
            "nomeSolicitante"               :ocorrencia.nom_solicita,
            "coUnidadePesquisa"             :"",
            "unidadePesquisada"             :"",
            "ocorrencia"                    :ocorrencia.numOcorrencia,
            "tipoOcorrencia"                :"3",
            "fase"                          :"2",
            "verificaPendecia"              :"0",
            "manifesto"                     :ocorrencia.manifesto,
            "comentario"                    :ocorrencia.comentario,
            "resposta"                      :"A ocorr&ecirc;ncia foi transferida indevidamente por falha tecnol&oacute;gica ap&oacute;s ter sido respondida pela unidade. A demanda foi respondida dentro do prazo. CEACR/BH",
            "respondidoPor"                 :matFechamento,
            "dataResposta"                  :datetime.now().strftime("%d/%m/%Y"),
            "nome"                          :ocorrencia.nom_solicita,
            "data"                          :datetime.now().strftime("%d/%m/%Y"),
            "hora"                          :datetime.now().strftime("%H:%M"),
            "meio"                          :"2"
        }
        try:
            respClose = self.nav.post("https://exemplo.com/ResponderOcorrencia.do?method=responderOcorrencia",params=parClose)
            if respClose.status_code==200:
                return True
        except Exception as e:
            self.lastError = format(e)
            pass
        return False

    def get_last_error(self):
        return self.lastError