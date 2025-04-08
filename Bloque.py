import hashlib
import time

class Bloque:
    
    def __init__(self, index, timestamp, votos, hash_anterior, hash_actual, tema_votacion="No especificado"):
        self.index = index
        self.timestamp = timestamp
        self.votos = votos
        self.hash_anterior = hash_anterior
        self.hash_actual = hash_actual
        self.tema_votacion = tema_votacion  # Nuevo atributo para el tema
    
    def calcular_hash(self):
        # Incluir el tema de votación en el cálculo del hash para garantizar la integridad
        bloque_string = str(self.index) + str(self.timestamp) + str(self.votos) + str(self.hash_anterior) + str(self.tema_votacion)
        return hashlib.sha256(bloque_string.encode()).hexdigest()
    
    @staticmethod
    def crear_bloque_genesis(tema_votacion="Bloque Génesis"):
        return Bloque(0, time.time(), [], "0", hashlib.sha256("genesis".encode()).hexdigest(), tema_votacion)
    
    @staticmethod
    def crear_nuevo_bloque(bloque_anterior, votos_pendientes, tema_votacion=None):
        index = bloque_anterior.index + 1
        timestamp = time.time()
        hash_anterior = bloque_anterior.hash_actual
        
        # Si no se proporciona un tema específico, hereda el del bloque anterior
        if tema_votacion is None:
            tema_votacion = bloque_anterior.tema_votacion
        
        nuevo_bloque = Bloque(index, timestamp, votos_pendientes, hash_anterior, "", tema_votacion)
        nuevo_bloque.hash_actual = nuevo_bloque.calcular_hash()
        return nuevo_bloque