class ClaseUsuario:
    __usuario = None
    def __init__(self):
        self.__usuario = None
    def __del__(self):
        self.__usuario = None
    
    def addusuario(self, usuario):
        self.__usuario = usuario
    
    def getUsuario(self):
        return self.__usuario