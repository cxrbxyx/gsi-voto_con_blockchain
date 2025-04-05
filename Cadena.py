import Bloque

class Cadena:
    def __init__(self):
        self.cadena = []
        self.votos_pendientes = []
        # Crear bloque génesis
        self.cadena.append(Bloque.Bloque.crear_bloque_genesis())
    
    def agregar_bloque(self, votos_nuevos=None):
        if votos_nuevos:
            self.votos_pendientes.extend(votos_nuevos)
            
        if len(self.votos_pendientes) > 0:
            bloque_anterior = self.peek()
            nuevo_bloque = Bloque.Bloque.crear_nuevo_bloque(bloque_anterior, self.votos_pendientes)
            if self.validar_bloque(nuevo_bloque):
                self.cadena.append(nuevo_bloque)
                self.votos_pendientes = []  # Limpiar votos pendientes
                return True
        return False
    
    def validar_bloque(self, bloque):
        if self.cadena_vacia():
            return True
        bloque_anterior = self.peek()
        if bloque.hash_anterior != bloque_anterior.hash_actual or bloque_anterior.index + 1 != bloque.index:
            print("Error en el bloque. Hash anterior no coincide o índice incorrecto")
            return False
        # Verificar que el hash calculado coincide
        hash_calculado = bloque.calcular_hash()
        if hash_calculado != bloque.hash_actual:
            print("Error en el bloque. Hash calculado no coincide")
            return False
        return True
    
    def cadena_vacia(self):
        return len(self.cadena) == 0
    
    def peek(self):
        if not self.cadena_vacia():
            return self.cadena[-1]
        return None
    
    def obtener_todos_votos(self):
        todos_votos = []
        for bloque in self.cadena:
            todos_votos.extend(bloque.votos)
        return todos_votos