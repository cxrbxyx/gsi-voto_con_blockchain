import Cadena
import time
import hashlib
import json

class SistemaVotacion:
    def __init__(self):
        self.cadena = Cadena.Cadena()
        self.votantes_registrados = {}  # {id_votante: {nombre, ha_votado}}
        self.candidatos = {}  # {id_candidato: nombre}
    
    def registrar_votante(self, id_votante, nombre):
        if id_votante in self.votantes_registrados:
            print(f"El votante con ID {id_votante} ya está registrado")
            return False
        
        self.votantes_registrados[id_votante] = {
            "nombre": nombre,
            "ha_votado": False
        }
        print(f"Votante {nombre} registrado correctamente con ID {id_votante}")
        return True
    
    def registrar_candidato(self, id_candidato, nombre):
        if id_candidato in self.candidatos:
            print(f"El candidato con ID {id_candidato} ya está registrado")
            return False
        
        self.candidatos[id_candidato] = nombre
        print(f"Candidato {nombre} registrado correctamente con ID {id_candidato}")
        return True
    
    def emitir_voto(self, id_votante, id_candidato):
        # Verificar si el votante está registrado
        if id_votante not in self.votantes_registrados:
            print("Votante no registrado")
            return False
        
        # Verificar si el votante ya ha votado
        if self.votantes_registrados[id_votante]["ha_votado"]:
            print("Este votante ya ha emitido su voto")
            return False
        
        # Verificar si el candidato existe
        if id_candidato not in self.candidatos:
            print("Candidato no registrado")
            return False
        
        # Crear un voto (manteniendo privacidad del votante)
        voto = {
            "timestamp": time.time(),
            "id_votante_hash": hashlib.sha256(str(id_votante).encode()).hexdigest(),
            "id_candidato": id_candidato
        }
        
        # Añadir voto a los pendientes y crear un bloque
        self.cadena.votos_pendientes.append(voto)
        self.votantes_registrados[id_votante]["ha_votado"] = True
        
        # Si hay suficientes votos, crear un nuevo bloque
        if len(self.cadena.votos_pendientes) >= 3:  # Por ejemplo, 3 votos por bloque
            if self.cadena.agregar_bloque():
                print("Voto registrado y nuevo bloque creado")
            else:
                print("Voto registrado, pendiente de inclusión en un bloque")
        else:
            print("Voto registrado, pendiente de inclusión en un bloque")
        
        return True
    
    def contar_votos(self):
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
    
    def mostrar_resultados(self):
        resultados = self.contar_votos()
        
        print("\n--- RESULTADOS DE LA VOTACIÓN ---")
        for id_candidato, votos in resultados.items():
            nombre_candidato = self.candidatos[id_candidato]
            print(f"{nombre_candidato}: {votos} votos")
        print("-------------------------------\n")
    
    def verificar_integridad_cadena(self):
        """Verifica que la cadena de bloques es válida"""
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

def menu():
    print("\n=== SISTEMA DE VOTACIÓN BLOCKCHAIN ===")
    print("1. Registrar nuevo votante")
    print("2. Registrar nuevo candidato")
    print("3. Emitir voto")
    print("4. Ver resultados actuales")
    print("5. Verificar integridad del blockchain")
    print("6. Crear nuevo bloque con votos pendientes")
    print("0. Salir")
    return input("Seleccione una opción: ")

def main():
    sistema = SistemaVotacion()
    
    # Añadir algunos candidatos de ejemplo
    sistema.registrar_candidato("C1", "María López")
    sistema.registrar_candidato("C2", "Juan Pérez")
    sistema.registrar_candidato("C3", "Ana García")
    
    while True:
        opcion = menu()
        
        if opcion == "1":
            id_votante = input("Ingrese ID del votante: ")
            nombre = input("Ingrese nombre del votante: ")
            sistema.registrar_votante(id_votante, nombre)
            
        elif opcion == "2":
            id_candidato = input("Ingrese ID del candidato: ")
            nombre = input("Ingrese nombre del candidato: ")
            sistema.registrar_candidato(id_candidato, nombre)
            
        elif opcion == "3":
            id_votante = input("Ingrese ID del votante: ")
            print("Candidatos disponibles:")
            for id_cand, nombre in sistema.candidatos.items():
                print(f"{id_cand}: {nombre}")
            id_candidato = input("Ingrese ID del candidato elegido: ")
            sistema.emitir_voto(id_votante, id_candidato)
            
        elif opcion == "4":
            sistema.mostrar_resultados()
            
        elif opcion == "5":
            if sistema.verificar_integridad_cadena():
                print("La cadena de bloques es íntegra y válida.")
            else:
                print("ALERTA: La cadena de bloques ha sido manipulada.")
                
        elif opcion == "6":
            if sistema.cadena.agregar_bloque():
                print("Nuevo bloque creado con los votos pendientes.")
            else:
                print("No hay votos pendientes para crear un nuevo bloque.")
                
        elif opcion == "0":
            print("Gracias por usar el sistema de votación blockchain")
            break
            
        else:
            print("Opción no válida")

if __name__ == "__main__":
    main()