import Bloque

class Cadena:
    def __init__(self, cadena):
        self.cadena = []

    def agregar_bloque(self, bloque):
        if self.validar_bloque(bloque):
            self.cadena.append(bloque)
    
    def validar_bloque(self,bloque):
        if self.cadena_vacia():
            return True
        bloque_anterior = self.peek()
        if bloque.hash_anterior != bloque_anterior.hash_actual or bloque_anterior.index + 1 != bloque.index:
            print("Error en el bloque. Hash anterior no coincide o indice incorrecto")
            return False
        return True
    
    def cadena_vacia(self):
        return len(self.cadena) == 0