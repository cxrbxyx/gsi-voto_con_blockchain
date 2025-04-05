import hashlib
import time

class Bloque:
    
    def __init__(self, index, timestamp, votos, hash_anterior, hash_actual):
        self.index = index
        self.timestamp = timestamp
        self.votos = votos
        self.hash_anterior = hash_anterior
        self.hash_actual = hash_actual
    
    def calcular_hash(self):
        bloque_string = str(self.index) + str(self.timestamp) + str(self.votos) + str(self.hash_anterior)
        return hashlib.sha256(bloque_string.encode()).hexdigest()
    
    @staticmethod
    def crear_bloque_genesis():
        return Bloque(0, time.time(), [], "0", hashlib.sha256("genesis".encode()).hexdigest())
    
    @staticmethod
    def crear_nuevo_bloque(bloque_anterior, votos_pendientes):
        index = bloque_anterior.index + 1
        timestamp = time.time()
        hash_anterior = bloque_anterior.hash_actual
        nuevo_bloque = Bloque(index, timestamp, votos_pendientes, hash_anterior, "")
        nuevo_bloque.hash_actual = nuevo_bloque.calcular_hash()
        return nuevo_bloque