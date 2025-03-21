import hashlib
import time

class Bloque:
    
    def __init__(self,index,timestamp,votos,hash_anterior,hash_actual):
        self.index = index
        self.timestamp = timestamp
        self.votos = votos
        self.hash_anterior = hash_anterior
        self.hash_actual = hash_actual
    
    def calcular_hash(self):
        bloque_string = str(self.index) + str(self.timestamp) + str(self.votos) + str(self.previous_hash)
        return hashlib.sha256(bloque_string.encode()).hexdigest()
    
    def crear_nuevo_bloque(bloque_anterior, votos_pendientes):
        index = bloque_anterior.index + 1
        timestamp = time.time()
        previous_hash = bloque_anterior.hash
        nuevo_bloque = Bloque(index, timestamp, votos_pendientes, previous_hash, "")
        nuevo_bloque.hash = nuevo_bloque.calcular_hash()
        return nuevo_bloque