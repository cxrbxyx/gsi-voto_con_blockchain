import Cadena
import Bloque
import time
import hashlib
import json
import os

class SistemaVotacion:
    ARCHIVO_DATOS = "blockchain_votacion.json"  # Nombre del archivo de datos

    def __init__(self):
        # Estado de la votación activa
        self.tema_activo = None
        self.candidatos_votacion_activa = {}  # {id_candidato: nombre} para la votación actual
        self.votos_sesion_actual = []  # Votos acumulados para el tema activo
        self.votantes_sesion_actual = set()  # Hashes de IDs de votantes que ya votaron en esta sesión
        self.ultimo_timestamp_archivo = 0 # Timestamp de la última carga/guardado conocido

        if os.path.exists(self.ARCHIVO_DATOS):
            if not self.cargar_datos():
                 # Si la carga inicial falla, inicializar vacío pero mantener timestamp 0
                 self._inicializar_vacio()
        else:
            self._inicializar_vacio()
            self.guardar_datos() # Guardar estado inicial y actualizar timestamp

    def _inicializar_vacio(self):
        """Método auxiliar para inicializar un estado vacío."""
        print("Inicializando sistema con estado vacío.")
        self.cadena = Cadena.Cadena()
        self.candidatos_globales = {}
        self.ultimo_id_candidato_global = -1
        self.tema_activo = None
        self.candidatos_votacion_activa = {}
        self.votos_sesion_actual = []
        self.votantes_sesion_actual = set()
        # No actualizamos timestamp aquí, se hará al guardar si es necesario

    def guardar_datos(self):
        """Guarda la cadena de bloques y los candidatos globales."""
        datos = {
            "candidatos_globales": self.candidatos_globales,
            "bloques": [self._serializar_bloque(bloque) for bloque in self.cadena.cadena],
            "ultimo_id_candidato_global": self.ultimo_id_candidato_global
        }
        try:
            with open(self.ARCHIVO_DATOS, 'w') as archivo:
                json.dump(datos, archivo, indent=2)
            # Actualizar el timestamp conocido después de guardar con éxito
            self.ultimo_timestamp_archivo = os.path.getmtime(self.ARCHIVO_DATOS)
            print(f"Datos guardados. Timestamp actualizado a: {self.ultimo_timestamp_archivo}")
            return True
        except Exception as e:
            print(f"Error al guardar datos: {str(e)}")
            return False

    def cargar_datos(self):
        """Carga la cadena, candidatos globales."""
        try:
            # Obtener timestamp ANTES de abrir, por si acaso
            timestamp_antes_carga = os.path.getmtime(self.ARCHIVO_DATOS)
            with open(self.ARCHIVO_DATOS, 'r') as archivo:
                datos = json.load(archivo)

            self.candidatos_globales = datos.get("candidatos_globales", {})
            self.ultimo_id_candidato_global = datos.get("ultimo_id_candidato_global", -1)

            self.cadena = Cadena.Cadena()
            self.cadena.cadena = []

            bloques_data = datos.get("bloques", [])
            if not bloques_data:
                print("No se encontraron bloques en el archivo, creando bloque génesis.")
                self.cadena.cadena.append(Bloque.Bloque.crear_bloque_genesis())
            else:
                for bloque_dict in bloques_data:
                    bloque = self._deserializar_bloque(bloque_dict)
                    self.cadena.cadena.append(bloque)

            if not self.cadena.cadena:
                print("Advertencia: La cadena está vacía después de cargar datos. Recreando bloque génesis.")
                self.cadena.cadena.append(Bloque.Bloque.crear_bloque_genesis())

            # Actualizar el timestamp conocido después de cargar con éxito
            self.ultimo_timestamp_archivo = timestamp_antes_carga
            print(f"Datos cargados. Timestamp actualizado a: {self.ultimo_timestamp_archivo}")

            # Reiniciar estado de sesión activa al cargar (si se mantiene esa lógica)
            print("Limpiando estado de votación activa debido a la carga de datos.")
            self.tema_activo = None
            self.candidatos_votacion_activa = {}
            self.votos_sesion_actual = []
            self.votantes_sesion_actual = set()

            return True
        # ... (resto del bloque except) ...
        except FileNotFoundError:
             print(f"Error: El archivo {self.ARCHIVO_DATOS} no fue encontrado durante la carga.")
             return False # Indicar fallo en la carga
        except json.JSONDecodeError as e:
             print(f"Error al decodificar JSON en {self.ARCHIVO_DATOS}: {str(e)}")
             return False # Indicar fallo en la carga
        except Exception as e:
            print(f"Error crítico al cargar datos: {str(e)}.")
            # No llamar a _inicializar_vacio aquí para evitar recursión si falla __init__
            return False # Indicar fallo en la carga


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

    def iniciar_votacion(self, tema):
        """Inicia una nueva sesión de votación para un tema específico."""
        if self.tema_activo:
            print(f"Error: Ya hay una votación activa para el tema '{self.tema_activo}'. Finalícela primero.")
            return False
        if not tema:
            print("Error: Se requiere un tema para iniciar la votación.")
            return False

        self.tema_activo = tema
        self.candidatos_votacion_activa = {}  # Reiniciar candidatos para la nueva votación
        self.votos_sesion_actual = []
        self.votantes_sesion_actual = set()
        print(f"Votación iniciada para el tema: '{self.tema_activo}'")
        return True

    def agregar_candidato_a_votacion(self, nombre_candidato):
        """Agrega un candidato a la votación activa."""
        if not self.tema_activo:
            print("Error: No hay ninguna votación activa para agregar candidatos.")
            return False
        if not nombre_candidato:
            print("Error: Se requiere un nombre para el candidato.")
            return False

        id_candidato_encontrado = None
        for id_cand, nombre in self.candidatos_globales.items():
            if nombre == nombre_candidato:
                id_candidato_encontrado = id_cand
                break

        if id_candidato_encontrado:
            id_candidato = id_candidato_encontrado
            print(f"Candidato '{nombre_candidato}' (ID: {id_candidato}) ya existe globalmente.")
        else:
            self.ultimo_id_candidato_global += 1
            id_candidato = str(self.ultimo_id_candidato_global)
            self.candidatos_globales[id_candidato] = nombre_candidato
            print(f"Candidato '{nombre_candidato}' registrado globalmente con ID {id_candidato}.")
            if not self.guardar_datos():
                print("ADVERTENCIA: No se pudo guardar el nuevo candidato global.")

        if id_candidato in self.candidatos_votacion_activa:
            print(f"Candidato '{nombre_candidato}' (ID: {id_candidato}) ya está añadido a la votación activa '{self.tema_activo}'.")
            return id_candidato

        self.candidatos_votacion_activa[id_candidato] = nombre_candidato
        print(f"Candidato '{nombre_candidato}' (ID: {id_candidato}) añadido a la votación activa '{self.tema_activo}'.")
        return id_candidato

    def emitir_voto_sesion(self, id_votante_externo, id_candidato):
        """Emite un voto para la sesión de votación activa."""
        if not self.tema_activo:
            print("Error: No hay ninguna votación activa para emitir votos.")
            return False
        if not id_votante_externo:
            print("Error: Se requiere la identificación del votante.")
            return False
        if id_candidato not in self.candidatos_votacion_activa:
            print(f"Error: Candidato con ID '{id_candidato}' no es válido para la votación activa '{self.tema_activo}'.")
            return False

        id_votante_hash = hashlib.sha256(str(id_votante_externo).encode()).hexdigest()

        
        for bloque in self.cadena.cadena[1:]: # Omitir bloque génesis
            if bloque.tema_votacion == self.tema_activo:
                for voto_en_bloque in bloque.votos:
                    if voto_en_bloque.get("id_votante_hash") == id_votante_hash:
                        print(f"Error: El votante con ID (hash) {id_votante_hash[:8]}... ya ha votado anteriormente para el tema '{self.tema_activo}' (encontrado en bloque {bloque.index}).")
                        return False
        

        # Verificar si el votante ya ha votado en la sesión actual
        if id_votante_hash in self.votantes_sesion_actual:
            print(f"Error: El votante con ID (hash) {id_votante_hash[:8]}... ya ha votado en esta sesión para '{self.tema_activo}'.")
            return False

        voto = {
            "timestamp": time.time(),
            "id_votante_hash": id_votante_hash,
            "id_candidato": id_candidato,
            "tema_votacion": self.tema_activo
        }
        self.votos_sesion_actual.append(voto)
        self.votantes_sesion_actual.add(id_votante_hash)

        print(f"Voto para '{self.tema_activo}' por votante {id_votante_hash[:8]}... registrado (pendiente de finalizar votación).")
        return True

    def finalizar_votacion(self):
        """Finaliza la votación activa, crea el bloque y lo añade a la cadena."""
        if not self.tema_activo:
            print("Error: No hay ninguna votación activa para finalizar.")
            return False
        if not self.votos_sesion_actual:
            print(f"Advertencia: No hay votos registrados para la votación '{self.tema_activo}'. No se creará un bloque.")
            self.tema_activo = None
            self.candidatos_votacion_activa = {}
            self.votos_sesion_actual = []
            self.votantes_sesion_actual = set()
            return False

        print(f"Finalizando votación para '{self.tema_activo}' con {len(self.votos_sesion_actual)} votos.")

        success = self.cadena.agregar_bloque(self.votos_sesion_actual, self.tema_activo)

        if success:
            print(f"Bloque para '{self.tema_activo}' añadido a la blockchain.")
            if not self.guardar_datos():
                print("ADVERTENCIA: No se pudieron guardar los datos después de añadir el bloque.")
            self.tema_activo = None
            self.candidatos_votacion_activa = {}
            self.votos_sesion_actual = []
            self.votantes_sesion_actual = set()
            return True
        else:
            print(f"Error: No se pudo añadir el bloque para '{self.tema_activo}' a la blockchain.")
            print("Se reseteará el estado de la votación activa debido al error.")
            self.tema_activo = None
            self.candidatos_votacion_activa = {}
            self.votos_sesion_actual = []
            self.votantes_sesion_actual = set()
            return False

    def registrar_candidato_global(self, nombre):
        """Registra un candidato globalmente si no existe."""
        if not nombre:
            return None
        for id_cand, nom in self.candidatos_globales.items():
            if nom == nombre:
                print(f"Candidato '{nombre}' ya existe globalmente con ID {id_cand}.")
                return id_cand
        self.ultimo_id_candidato_global += 1
        id_candidato = str(self.ultimo_id_candidato_global)
        self.candidatos_globales[id_candidato] = nombre
        print(f"Candidato '{nombre}' registrado globalmente con ID {id_candidato}.")
        if not self.guardar_datos():
            print("ADVERTENCIA: No se pudo guardar el nuevo candidato global.")
        return id_candidato

    def contar_votos(self, tema_especifico=None):
        """Cuenta votos globalmente o para un tema específico."""
        try:
            resultados = {id_candidato: 0 for id_candidato in self.candidatos_globales}
            votos_a_contar = []

            for bloque in self.cadena.cadena[1:]:
                if tema_especifico is None or bloque.tema_votacion == tema_especifico:
                    votos_a_contar.extend(bloque.votos)

            for voto in votos_a_contar:
                id_candidato = voto.get("id_candidato")
                if id_candidato in resultados:
                    resultados[id_candidato] += 1

            if self.tema_activo and (tema_especifico is None or self.tema_activo == tema_especifico):
                print(f"Incluyendo {len(self.votos_sesion_actual)} votos pendientes de la sesión activa '{self.tema_activo}'.")
                for voto_pendiente in self.votos_sesion_actual:
                    id_candidato = voto_pendiente.get("id_candidato")
                    if id_candidato in resultados:
                        resultados[id_candidato] += 1

            resultados_filtrados = {id_c: v for id_c, v in resultados.items() if v > 0}
            return resultados_filtrados
        except Exception as e:
            print(f"Error al contar votos: {str(e)}")
            return {}

    def mostrar_resultados(self, tema_especifico=None):
        """Muestra los resultados globales o para un tema específico."""
        try:
            resultados = self.contar_votos(tema_especifico)
            titulo_tema = f"para el tema '{tema_especifico}'" if tema_especifico else "globales"

            print(f"\n--- RESULTADOS DE LA VOTACIÓN ({titulo_tema}) ---")
            if not resultados:
                print("No hay votos registrados para mostrar.")
            else:
                resultados_ordenados = sorted(resultados.items(), key=lambda item: item[1], reverse=True)
                for id_candidato, votos in resultados_ordenados:
                    nombre_candidato = self.candidatos_globales.get(id_candidato, f"ID Desconocido {id_candidato}")
                    print(f"{nombre_candidato} (ID: {id_candidato}): {votos} votos")
            print("-------------------------------------------\n")
            return True
        except Exception as e:
            print(f"Error al mostrar resultados: {str(e)}")
            return False

    def verificar_integridad_cadena(self):
        """Verifica la integridad de la cadena en memoria, advirtiendo si el archivo externo ha cambiado."""
        try:
            # --- INICIO COMPROBACIÓN DE MODIFICACIÓN EXTERNA ---
            try:
                timestamp_actual_archivo = os.path.getmtime(self.ARCHIVO_DATOS)
                if timestamp_actual_archivo != self.ultimo_timestamp_archivo:
                    print("\n" + "="*60)
                    print("¡ADVERTENCIA! El archivo blockchain_votacion.json ha sido modificado")
                    print("externamente desde la última carga o guardado realizado por la aplicación.")
                    print(f"  - Timestamp conocido: {self.ultimo_timestamp_archivo}")
                    print(f"  - Timestamp actual:   {timestamp_actual_archivo}")
                    print("La verificación de integridad se realizará sobre los datos en MEMORIA,")
                    print("que podrían no reflejar el contenido actual del archivo.")
                    print("Considere reiniciar la aplicación para recargar desde el archivo si es necesario.")
                    print("="*60 + "\n")
            except FileNotFoundError:
                 print("\nADVERTENCIA: No se encontró el archivo blockchain_votacion.json para comprobar su modificación.\n")
            except Exception as e:
                 print(f"\nADVERTENCIA: No se pudo comprobar la fecha de modificación del archivo: {e}\n")
            # --- FIN COMPROBACIÓN DE MODIFICACIÓN EXTERNA ---

            # Ahora procede la verificación sobre los datos en memoria (self.cadena.cadena)
            # 1. Verificar si la cadena está vacía
            if not self.cadena.cadena:
                 print("Error de integridad (Memoria): La cadena está completamente vacía.")
                 return False

            # 2. Verificar el Bloque Génesis
            primer_bloque = self.cadena.cadena[0]
            if primer_bloque.index != 0:
                print(f"Error de integridad (Memoria): El primer bloque no es el Génesis (índice {primer_bloque.index} en lugar de 0).")
                return False
            if primer_bloque.hash_anterior != "0":
                 print(f"Error de integridad (Memoria): El hash anterior del bloque Génesis no es '0'.")
                 # return False # Descomentar si se considera crítico

            # 3. Verificar el resto de los bloques
            if len(self.cadena.cadena) <= 1:
                print("Integridad (Memoria): Cadena solo con bloque génesis, se considera íntegra.")
                return True

            for i in range(1, len(self.cadena.cadena)):
                bloque_actual = self.cadena.cadena[i]
                bloque_anterior = self.cadena.cadena[i - 1]

                if bloque_actual.index != i:
                     print(f"Error de integridad (Memoria): Índice incorrecto en la posición {i}. Esperado {i}, encontrado {bloque_actual.index}.")
                     return False
                if bloque_actual.hash_anterior != bloque_anterior.hash_actual:
                    print(f"Error de integridad (Memoria): Hash anterior del bloque {bloque_actual.index} no coincide.")
                    return False
                if bloque_actual.hash_actual != bloque_actual.calcular_hash():
                    print(f"Error de integridad (Memoria): Hash actual del bloque {bloque_actual.index} es inválido.")
                    return False

            print("Verificación de integridad (Memoria) completada: La cadena en memoria es válida.")
            return True
        except Exception as e:
            print(f"Error durante la verificación de integridad: {str(e)}")
            return False

    def mostrar_estructura_cadena(self):
        """Muestra la estructura de la cadena."""
        try:
            print("\n=== ESTRUCTURA DE LA CADENA DE BLOQUES ===")
            if len(self.cadena.cadena) == 0:
                print("La cadena está vacía.")
                return True
            if len(self.cadena.cadena) == 1:
                print("La cadena solo contiene el bloque Génesis.")

            for i, bloque in enumerate(self.cadena.cadena):
                print(f"\n----- BLOQUE #{i} -----")
                print(f"Índice: {bloque.index}")
                print(f"Tema de votación: {bloque.tema_votacion}")
                try:
                    timestamp_legible = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(bloque.timestamp))
                except ValueError:
                    timestamp_legible = f"Timestamp inválido ({bloque.timestamp})"
                print(f"Timestamp: {timestamp_legible}")
                print(f"Hash: {bloque.hash_actual}")
                print(f"Hash anterior: {bloque.hash_anterior}")
                print(f"Número de votos: {len(bloque.votos)}")

                if len(bloque.votos) > 0:
                    print("  Resumen de votos en este bloque:")
                    votos_por_candidato = {}
                    for voto in bloque.votos:
                        id_candidato = voto.get("id_candidato")
                        nombre = self.candidatos_globales.get(id_candidato, f"ID {id_candidato}")
                        votos_por_candidato[nombre] = votos_por_candidato.get(nombre, 0) + 1

                    for candidato, num_votos in votos_por_candidato.items():
                        print(f"    - {candidato}: {num_votos} votos")

            print("\n=========================================")
            return True
        except Exception as e:
            print(f"Error al mostrar estructura de la cadena: {str(e)}")
            return False

    def obtener_estado_votacion_activa(self):
        """Devuelve información sobre la votación activa."""
        if not self.tema_activo:
            return None
        return {
            "tema_activo": self.tema_activo,
            "candidatos": self.candidatos_votacion_activa,
            "numero_votos_recibidos": len(self.votos_sesion_actual),
            "numero_votantes_participantes": len(self.votantes_sesion_actual)
        }