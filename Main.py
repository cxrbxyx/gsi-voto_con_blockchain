from SistemaVotacion import SistemaVotacion

def menu():
    print("\n=== SISTEMA DE VOTACIÓN BLOCKCHAIN ===")
    print("1. Registrar nuevo votante")
    print("2. Registrar nuevo candidato")
    print("3. Emitir voto")
    print("4. Ver resultados actuales")
    print("5. Verificar integridad del blockchain")
    print("6. Crear nuevo bloque con votos pendientes")
    print("7. Mostrar estructura de la cadena")
    print("8. Listar votantes registrados")
    print("9. Listar candidatos disponibles")
    print("0. Salir")
    return input("Seleccione una opción: ")

def main():
    try:
        sistema = SistemaVotacion()
            
        while True:
            opcion = menu()
            
            if opcion == "1":
                try:
                    nombre = input("Introduzca nombre del votante: ")
                    sistema.registrar_votante(nombre)
                except Exception as e:
                    print(f"Error: {str(e)}")
                
            elif opcion == "2":
                try:
                    nombre = input("Introduzca nombre del candidato: ")
                    sistema.registrar_candidato(nombre)
                except Exception as e:
                    print(f"Error: {str(e)}")
                
            elif opcion == "3":
                try:
                    # Preguntar si quiere usar un tema específico para esta votación
                    print("\nEmisión de voto:")
                    usar_tema = input("¿Desea especificar un tema para esta votación? (s/n): ").lower()
                    
                    tema_votacion = None
                    if usar_tema == 's':
                        tema_votacion = input("Introduzca el tema de la votación: ")
                        
                    # Mostrar lista de votantes
                    print("\nVotantes registrados:")
                    votantes_disponibles = []
                    
                    for id_votante, datos in sistema.votantes_registrados.items():
                        # Si no hay tema específico, usar el tema general
                        tema_actual = tema_votacion if tema_votacion is not None else sistema.cadena.tema_votacion
                        
                        # Verificar si el votante ya votó en este tema
                        ya_voto = tema_actual in datos["temas_votados"]
                        estado = f"Ya ha votado en '{tema_actual}'" if ya_voto else "No ha votado en este tema"
                        
                        print(f"ID: {id_votante}, Nombre: {datos['nombre']} - {estado}")
                        
                        if not ya_voto:
                            votantes_disponibles.append(id_votante)
                    
                    if not votantes_disponibles:
                        print("\nNo hay votantes disponibles para esta votación.")
                        continue
                        
                    id_votante = input("\nIntroduzca ID del votante: ")
                    
                    # Verificar si el votante existe
                    if id_votante not in sistema.votantes_registrados:
                        print("Error: ID de votante no válido")
                        continue
                    
                    # Verificar si ya votó en este tema
                    tema_actual = tema_votacion if tema_votacion is not None else sistema.cadena.tema_votacion
                    if tema_actual in sistema.votantes_registrados[id_votante]["temas_votados"]:
                        print(f"Error: Este votante ya emitió su voto en la votación '{tema_actual}'")
                        continue
                    
                    # Mostrar candidatos disponibles
                    print("\nCandidatos disponibles:")
                    for id_cand, nombre in sistema.candidatos.items():
                        print(f"ID: {id_cand}, Nombre: {nombre}")
                    
                    id_candidato = input("\Introduzca ID del candidato elegido: ")
                    sistema.emitir_voto(id_votante, id_candidato, tema_votacion)
                except Exception as e:
                    print(f"Error: {str(e)}")
                
            elif opcion == "4":
                sistema.mostrar_resultados()
                
            elif opcion == "5":
                if sistema.verificar_integridad_cadena():
                    print("La cadena de bloques es íntegra y válida.")
                else:
                    print("ALERTA: La cadena de bloques ha sido manipulada.")
                    
            elif opcion == "6":
                try:
                    # Preguntar por el tema de la votación
                    print("\nCreación de nuevo bloque:")
                    usar_tema = input("¿Desea especificar un tema para esta votación? (s/n): ").lower()
                    
                    if usar_tema == 's':
                        tema = input("Introduzca el tema de la votación: ")
                        if sistema.crear_nuevo_bloque(tema_votacion=tema):
                            print(f"Nuevo bloque creado con los votos pendientes. Tema: '{tema}'")
                        else:
                            print("No hay votos pendientes para crear un nuevo bloque.")
                    else:
                        if sistema.crear_nuevo_bloque():
                            print("Nuevo bloque creado con los votos pendientes.")
                        else:
                            print("No hay votos pendientes para crear un nuevo bloque.")
                except Exception as e:
                    print(f"Error al crear bloque: {str(e)}")
            
            elif opcion == "7":
                sistema.mostrar_estructura_cadena()
            
            elif opcion == "8":
                # Mostrar lista de todos los votantes
                print("\n--- VOTANTES REGISTRADOS ---")
                if len(sistema.votantes_registrados) == 0:
                    print("No hay votantes registrados.")
                else:
                    for id_votante, datos in sistema.votantes_registrados.items():
                        print(f"ID: {id_votante}, Nombre: {datos['nombre']}")
                        if datos["temas_votados"]:
                            print("  Ha votado en los siguientes temas:")
                            for tema in datos["temas_votados"]:
                                print(f"  - {tema}")
                        else:
                            print("  No ha participado en ninguna votación")
                print("---------------------------\n")
            
            elif opcion == "9":
                # Mostrar lista de todos los candidatos
                print("\n--- CANDIDATOS DISPONIBLES ---")
                if len(sistema.candidatos) == 0:
                    print("No hay candidatos registrados.")
                else:
                    for id_cand, nombre in sistema.candidatos.items():
                        print(f"ID: {id_cand}, Nombre: {nombre}")
                print("-----------------------------\n")
                    
            elif opcion == "0":
                sistema.resetear_estado_votantes()
                print("Gracias por usar el sistema de votación blockchain")
                break
                
            else:
                print("Opción no válida")
    
    except Exception as e:
        print(f"Error crítico: {str(e)}")
        print("El programa se cerrará.")

if __name__ == "__main__":
    main()