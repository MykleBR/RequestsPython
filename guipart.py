import tkinter
from tkinter import ttk

class GuiPart:
    lineCounter = 1 #contador para as linhas de mensagens que serao exibidas na tela
    def __init__(self,master,queue):
        self.queue  = queue
        self.master = master
        self.create_widgets()
        self.processIncoming()
            
    def create_widgets(self):
        """Metodo que monta os objetos de tela
        """
        #cria um frame no topo com 50 px de altura para armazenar os items do login
        frameLogin = tkinter.Frame(self.master,padx=0,pady=5)
        frameLogin.pack(fill=tkinter.X)

        #cria um frame npara armazenar os items de texto
        frameTexto = tkinter.Frame(self.master)
        frameTexto.pack(fill='both',expand=1)

        #cria um frame para armazenar a progressbar
        frameBar = tkinter.Frame(self.master)
        frameBar.pack(fill=tkinter.X)

        #cria um label para colocar a data inicial de execucao do sistema
        self.lblDesc = tkinter.Label(frameLogin,text="Robô")
        self.lblDesc.pack(side=tkinter.LEFT)

        #cria um text para resultado dos logs (precisa ser self pois eh usado em outro metodo)
        self.txtResult = tkinter.Text(frameTexto)
        self.txtResult.pack(side=tkinter.LEFT,expand=True,fill='both')
        
        #cria um scrollbar para a rolagem do text
        scrl = tkinter.Scrollbar(frameTexto,command=self.txtResult.yview)
        scrl.pack(side=tkinter.RIGHT,fill=tkinter.Y)

        #cria um progressbar para deixar bonita a exibicao  (precisa ser self pois eh usado em outro metodo)
        self.progress = ttk.Progressbar(frameBar,orient='horizontal',mode='determinate',length=630)
        self.progress.pack(fill=tkinter.BOTH)
        self.txtResult["yscrollcommand"] = scrl.set

        #cores das linhas para exibir nas mensagens de tela
        self.txtResult.tag_config('RED'     ,foreground='#FF0000')
        self.txtResult.tag_config('GREEN'   ,foreground='#006400')
        self.txtResult.tag_config('ORANGE'  ,foreground='#FF8C00')
        self.txtResult.tag_config('PURPLE'  ,foreground='#A020F0')
        self.txtResult.tag_config('INDIGO'  ,foreground='#4B0082') 
        self.txtResult.tag_config('BROWN'   ,foreground='#8B4513')
        self.txtResult.tag_config('TOMATO'  ,foreground='#FF6347')
        self.txtResult.tag_config('BLUE'    ,foreground='#4169e1')

    def processIncoming(self):
        """Metodo que envia a mensagem para a tela ou para o log
        """
        while self.queue.qsize():
            que = self.queue.get()
            msg = que[0]
            cor = que[1]
                
            self.lineCounter += 1
            if cor!=None:
                self.txtResult.insert(str(self.lineCounter)+'.0',str(msg)+'\n',cor)
            else:
                self.txtResult.insert(str(self.lineCounter)+'.0',str(msg)+'\n')
            self.txtResult.see("end")
                
        self.master.after(200,self.processIncoming)