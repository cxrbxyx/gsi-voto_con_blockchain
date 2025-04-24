import Bloque

class Cadena:
    def __init__(self, tema_votacion="Votación General"):
        self.cadena = []
        self.tema_votacion = tema_votacion
        self.cadena.append(Bloque.Bloque.crear_bloque_genesis(self.tema_votacion))

    def agregar_bloque(self, votos_nuevos, tema_votacion):
        """
        Agrega un nuevo bloque directamente con los votos proporcionados y un tema específico.
        Ya no usa votos_pendientes internos.
        """
        if not votos_nuevos:
            print("No se proporcionaron votos para crear el bloque.")
            return False

        bloque_anterior = self.peek()
        if not bloque_anterior:
            print("Error: No se puede agregar bloque, la cadena parece vacía o corrupta después del génesis.")
            return False

        if tema_votacion is None:
            print("Error: Se requiere un tema de votación para crear un nuevo bloque.")
            return False

        nuevo_bloque = Bloque.Bloque.crear_nuevo_bloque(bloque_anterior, votos_nuevos, tema_votacion)

        if self.validar_bloque(nuevo_bloque):
            self.cadena.append(nuevo_bloque)
            print(f"Bloque para el tema '{tema_votacion}' agregado correctamente.")
            return True
        else:
            print(f"Error de validación al intentar agregar bloque para '{tema_votacion}'.")
            return False

    def validar_bloque(self, bloque):
        if self.cadena_vacia():
            print("Advertencia: Validando bloque en una cadena supuestamente vacía.")
            return True
        bloque_anterior = self.peek()
        if not bloque_anterior:
            print("Error crítico: No se encontró el bloque anterior para validar.")
            return False
        if bloque.hash_anterior != bloque_anterior.hash_actual or bloque_anterior.index + 1 != bloque.index:
            print(f"Error en el bloque {bloque.index}. Hash anterior no coincide ({bloque.hash_anterior} vs {bloque_anterior.hash_actual}) o índice incorrecto.")
            return False
        hash_calculado = bloque.calcular_hash()
        if hash_calculado != bloque.hash_actual:
            print(f"Error en el bloque {bloque.index}. Hash calculado ({hash_calculado}) no coincide con el almacenado ({bloque.hash_actual}).")
            return False
        return True

    def cadena_vacia(self):
        return len(self.cadena) <= 1

    def peek(self):
        if self.cadena:
            return self.cadena[-1]
        return None

    def obtener_todos_votos(self):
        todos_votos = []
        for bloque in self.cadena[1:]:
            todos_votos.extend(bloque.votos)
        return todos_votos