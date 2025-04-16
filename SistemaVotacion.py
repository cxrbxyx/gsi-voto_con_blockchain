import Cadena
import Bloque
import time
import hashlib
import json
import os



class SistemaVotacion:
    ARCHIVO_DATOS = "blockchain_votacion.json"
    
    def __init__(self):
        # Intentar cargar datos existentes, o crear nuevos si no existen
        if os.path.exists(self.ARCHIVO_DATOS):
            self.cargar_datos()
        else:
            self.cadena = Cadena.Cadena()
            self.votantes_registrados = {}  # {id_votante: {nombre, temas_votados}}
            self.candidatos = {}  # {id_candidato: nombre}
            self.ultimo_id_votante = -1  # Para generar IDs autoincrementales
            self.ultimo_id_candidato = -1  # Para generar IDs autoincrementales
            self.guardar_datos()  # Guardar estado inicial
    
    def guardar_datos(self):
        """Guarda el estado actual del sistema en un archivo JSON"""
        datos = {
            "candidatos": self.candidatos,
            "votantes": self.votantes_registrados,
            "bloques": [self._serializar_bloque(bloque) for bloque in self.cadena.cadena],
            "votos_pendientes": self.cadena.votos_pendientes,
            "ultimo_id_votante": self.ultimo_id_votante,
            "ultimo_id_candidato": self.ultimo_id_candidato
        }
        
        try:
            with open(self.ARCHIVO_DATOS, 'w') as archivo:
                json.dump(datos, archivo, indent=2)
            return True
        except Exception as e:
            print(f"Error al guardar datos: {str(e)}")
            return False
        
    def cargar_datos(self):
        """Carga los datos del sistema desde un archivo JSON"""
        try:
            with open(self.ARCHIVO_DATOS, 'r') as archivo:
                datos = json.load(archivo)
            
            self.candidatos = datos.get("candidatos", {})
            self.votantes_registrados = datos.get("votantes", {})
            self.ultimo_id_votante = datos.get("ultimo_id_votante", -1)
            self.ultimo_id_candidato = datos.get("ultimo_id_candidato", -1)
            
            # Recrear la cadena con los bloques almacenados
            self.cadena = Cadena.Cadena()
            self.cadena.cadena = []  # Limpiar el bloque génesis automático
            
            for bloque_dict in datos.get("bloques", []):
                bloque = self._deserializar_bloque(bloque_dict)
                self.cadena.cadena.append(bloque)
                
            self.cadena.votos_pendientes = datos.get("votos_pendientes", [])
            return True
        except Exception as e:
            print(f"Error al cargar datos: {str(e)}")
            self.cadena = Cadena.Cadena()
            self.votantes_registrados = {}
            self.candidatos = {}
            self.ultimo_id_votante = -1
            self.ultimo_id_candidato = -1
            return False
    
    def _serializar_bloque(self, bloque):
        """Convierte un objeto Bloque en un diccionario para JSON"""
        return {
            "index": bloque.index,
            "timestamp": bloque.timestamp,
            "votos": bloque.votos,
            "hash_anterior": bloque.hash_anterior,
            "hash_actual": bloque.hash_actual,
            "tema_votacion": bloque.tema_votacion
        }
    
    def _deserializar_bloque(self, bloque_dict):
        """Convierte un diccionario en un objeto Bloque"""
        return Bloque.Bloque(
            index=bloque_dict["index"],
            timestamp=bloque_dict["timestamp"],
            votos=bloque_dict["votos"],
            hash_anterior=bloque_dict["hash_anterior"],
            hash_actual=bloque_dict["hash_actual"],
            tema_votacion=bloque_dict.get("tema_votacion", "No especificado")
        )
    
    def generar_id_votante(self):
        """Genera un nuevo ID único para un votante"""
        self.ultimo_id_votante += 1
        return str(self.ultimo_id_votante)
    
    def generar_id_candidato(self):
        """Genera un nuevo ID único para un candidato"""
        self.ultimo_id_candidato += 1
        return str(self.ultimo_id_candidato)
    
    def registrar_votante(self, nombre):
        """Registra un nuevo votante con un ID autogenerado"""
        try:
            id_votante = self.generar_id_votante()
            
            self.votantes_registrados[id_votante] = {
                "nombre": nombre,
                "temas_votados": []  # Lista de temas en los que ha votado
            }
            
            print(f"Votante {nombre} registrado correctamente con ID {id_votante}")
            if not self.guardar_datos():
                print("ADVERTENCIA: No se pudieron guardar los cambios en el archivo")
            
            return id_votante
        except Exception as e:
            print(f"Error al registrar votante: {str(e)}")
            return None
    
    def registrar_candidato(self, nombre):
        """Registra un nuevo candidato con un ID autogenerado"""
        try:
            id_candidato = self.generar_id_candidato()
            
            self.candidatos[id_candidato] = nombre
            
            print(f"Candidato {nombre} registrado correctamente con ID {id_candidato}")
            if not self.guardar_datos():
                print("ADVERTENCIA: No se pudieron guardar los cambios en el archivo")
            
            return id_candidato
        except Exception as e:
            print(f"Error al registrar candidato: {str(e)}")
            return None
    
    def emitir_voto(self, id_votante, id_candidato, tema_votacion=None):
        """Emite un voto verificando que el votante y candidato existan"""
        try:
            # Verificar si el votante está registrado
            if id_votante not in self.votantes_registrados:
                print("Error: Votante no registrado")
                return False
            
            # Obtener tema de la votación (si no se especifica, usar el tema general)
            tema_actual = tema_votacion if tema_votacion is not None else self.cadena.tema_votacion
            
            # Verificar si el votante ya ha votado en este tema
            if tema_actual in self.votantes_registrados[id_votante]["temas_votados"]:
                print(f"Error: Este votante ya ha emitido su voto en la votación '{tema_actual}'")
                return False
            
            # Verificar si el candidato existe
            if id_candidato not in self.candidatos:
                print("Error: Candidato no registrado")
                return False
            
            # Crear un voto (manteniendo privacidad del votante)
            voto = {
                "timestamp": time.time(),
                "id_votante_hash": hashlib.sha256(str(id_votante).encode()).hexdigest(),
                "id_candidato": id_candidato,
                "tema_votacion": tema_actual
            }
            
            # Añadir voto a los pendientes y registrar que el votante ha participado en este tema
            self.cadena.votos_pendientes.append(voto)
            self.votantes_registrados[id_votante]["temas_votados"].append(tema_actual)
            
            # Si hay suficientes votos, crear un nuevo bloque
            if len(self.cadena.votos_pendientes) >= 3:  # Por ejemplo, 3 votos por bloque
                if self.cadena.agregar_bloque(tema_votacion=tema_actual):
                    print(f"Voto registrado en '{tema_actual}' y nuevo bloque creado")
                else:
                    print(f"Voto registrado en '{tema_actual}', pendiente de inclusión en un bloque")
            else:
                print(f"Voto registrado en '{tema_actual}', pendiente de inclusión en un bloque")
            
            if not self.guardar_datos():
                print("ADVERTENCIA: No se pudieron guardar los cambios en el archivo")
            
            return True
        except Exception as e:
            print(f"Error al emitir voto: {str(e)}")
            return False
    
    # El resto de métodos quedan igual pero con control de errores

    def contar_votos(self):
        try:
            resultados = {id_candidato: 0 for id_candidato in self.candidatos}
            
            todos_votos = self.cadena.obtener_todos_votos()
            votos_pendientes = self.cadena.votos_pendientes
            
            # Contar votos en bloques confirmados
            for voto in todos_votos:
                if voto.get("id_candidato") in resultados:
                    resultados[voto["id_candidato"]] += 1
            
            # Contar votos pendientes
            for voto in votos_pendientes:
                if voto.get("id_candidato") in resultados:
                    resultados[voto["id_candidato"]] += 1
            
            return resultados
        except Exception as e:
            print(f"Error al contar votos: {str(e)}")
            return {}
    
    def mostrar_resultados(self):
        try:
            resultados = self.contar_votos()
            
            print("\n--- RESULTADOS DE LA VOTACIÓN ---")
            for id_candidato, votos in resultados.items():
                nombre_candidato = self.candidatos[id_candidato]
                print(f"{nombre_candidato}: {votos} votos")
            print("-------------------------------\n")
            return True
        except Exception as e:
            print(f"Error al mostrar resultados: {str(e)}")
            return False
    
    def verificar_integridad_cadena(self):
        """Verifica que la cadena de bloques es válida"""
        try:
            for i in range(1, len(self.cadena.cadena)):
                bloque_actual = self.cadena.cadena[i]
                bloque_anterior = self.cadena.cadena[i-1]
                
                # Verificar hash del bloque anterior
                if bloque_actual.hash_anterior != bloque_anterior.hash_actual:
                    return False
                
                # Verificar hash del bloque actual
                if bloque_actual.hash_actual != bloque_actual.calcular_hash():
                    return False
            
            return True
        except Exception as e:
            print(f"Error al verificar integridad: {str(e)}")
            return False
    
    def crear_nuevo_bloque(self, tema_votacion=None):
        """Crea un nuevo bloque con los votos pendientes"""
        try:
            if self.cadena.agregar_bloque(tema_votacion=tema_votacion):
                if not self.guardar_datos():
                    print("ADVERTENCIA: No se pudieron guardar los cambios en el archivo")
                return True
            return False
        except Exception as e:
            print(f"Error al crear nuevo bloque: {str(e)}")
            return False

    def mostrar_estructura_cadena(self):
        """
        Muestra la estructura completa de la cadena de bloques,
        incluyendo información detallada de cada bloque.
        """
        try:
            print("\n=== ESTRUCTURA DE LA CADENA DE BLOQUES ===")
            
            if len(self.cadena.cadena) == 0:
                print("La cadena está vacía.")
                return True
            
            for i, bloque in enumerate(self.cadena.cadena):
                print(f"\n----- BLOQUE #{i} -----")
                print(f"Índice: {bloque.index}")
                print(f"Tema de votación: {bloque.tema_votacion}")
                print(f"Timestamp: {time.ctime(bloque.timestamp)}")
                print(f"Hash: {bloque.hash_actual[:15]}...") # Mostramos parte del hash para legibilidad
                print(f"Hash anterior: {bloque.hash_anterior[:15]}...")
                
                print(f"Número de votos: {len(bloque.votos)}")
                
                if len(bloque.votos) > 0:
                    print("Resumen de votos:")
                    votos_por_candidato = {}
                    for voto in bloque.votos:
                        id_candidato = voto.get("id_candidato")
                        if id_candidato in self.candidatos:
                            nombre = self.candidatos[id_candidato]
                            if nombre not in votos_por_candidato:
                                votos_por_candidato[nombre] = 0
                            votos_por_candidato[nombre] += 1
                    
                    for candidato, num_votos in votos_por_candidato.items():
                        print(f"  - {candidato}: {num_votos} votos")
            
            print("\n----- VOTOS PENDIENTES -----")
            print(f"Número de votos pendientes: {len(self.cadena.votos_pendientes)}")
            
            if len(self.cadena.votos_pendientes) > 0:
                votos_pendientes_por_candidato = {}
                for voto in self.cadena.votos_pendientes:
                    id_candidato = voto.get("id_candidato")
                    if id_candidato in self.candidatos:
                        nombre = self.candidatos[id_candidato]
                        if nombre not in votos_pendientes_por_candidato:
                            votos_pendientes_por_candidato = 0
                        votos_pendientes_por_candidato[nombre] += 1
                
                for candidato, num_votos in votos_pendientes_por_candidato.items():
                    print(f"  - {candidato}: {num_votos} votos")
            
            print("\n=========================================")
            return True
        except Exception as e:
            print(f"Error al mostrar estructura de la cadena: {str(e)}")
            return False
    
    def resetear_estado_votantes(self):
        """
        Resetea los temas en los que han votado los votantes
        para permitir votar de nuevo en una nueva ejecución.
        """
        try:
            cambios = False
            for id_votante in self.votantes_registrados:
                if self.votantes_registrados[id_votante]["temas_votados"]:
                    self.votantes_registrados[id_votante]["temas_votados"] = []
                    cambios = True
            
            if cambios:
                print("\nSe ha restablecido el estado de votación de todos los votantes.")
                if not self.guardar_datos():
                    print("ADVERTENCIA: No se pudieron guardar los cambios en el archivo")
                return True
            return False
        except Exception as e:
            print(f"Error al resetear estado de votantes: {str(e)}")
            return False