from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import SistemaVotacion
import os

# Determinar la ruta absoluta al directorio del frontend
frontend_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
template_folder = os.path.join(frontend_folder, 'templates')
static_folder = os.path.join(frontend_folder, 'static')

# Verificar si las carpetas existen
if not os.path.isdir(template_folder):
    print(f"Error: La carpeta de plantillas no existe en {template_folder}")
    # Podrías decidir salir o continuar sin plantillas
if not os.path.isdir(static_folder):
    print(f"Error: La carpeta de archivos estáticos no existe en {static_folder}")
    # Podrías decidir salir o continuar sin archivos estáticos

app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
CORS(app) # Habilitar CORS para todas las rutas

# Crear una instancia única del sistema de votación
sistema_votacion = SistemaVotacion.SistemaVotacion()

# --- Rutas para la Gestión de la Votación Activa ---

@app.route('/votacion/iniciar', methods=['POST'])
def iniciar_votacion_api():
    """Inicia una nueva sesión de votación con un tema."""
    data = request.get_json()
    tema = data.get('tema')
    if not tema:
        return jsonify({"error": "Se requiere el campo 'tema'"}), 400

    if sistema_votacion.iniciar_votacion(tema):
        return jsonify({"mensaje": f"Votación iniciada para el tema: '{tema}'"}), 200
    else:
        # El método iniciar_votacion ya imprime errores específicos
        # Podríamos capturar esos mensajes si quisiéramos devolverlos aquí
        return jsonify({"error": "No se pudo iniciar la votación (verifique si ya hay una activa)"}), 409 # Conflict

@app.route('/votacion/candidato', methods=['POST'])
def agregar_candidato_api():
    """Agrega un candidato a la votación activa."""
    if not sistema_votacion.tema_activo:
         return jsonify({"error": "No hay ninguna votación activa"}), 400

    data = request.get_json()
    nombre_candidato = data.get('nombre')
    if not nombre_candidato:
        return jsonify({"error": "Se requiere el campo 'nombre' del candidato"}), 400

    id_candidato = sistema_votacion.agregar_candidato_a_votacion(nombre_candidato)
    if id_candidato is not None:
         # Devolvemos el ID y nombre para referencia en el frontend
        return jsonify({
            "mensaje": f"Candidato '{nombre_candidato}' añadido/confirmado en la votación '{sistema_votacion.tema_activo}'",
            "id_candidato": id_candidato,
            "nombre_candidato": nombre_candidato
            }), 200 # O 201 si siempre es nuevo, pero puede reutilizar global
    else:
        # El método interno ya imprime errores
        return jsonify({"error": "No se pudo agregar el candidato a la votación activa"}), 500

@app.route('/votacion/votar', methods=['POST'])
def votar_en_sesion_api():
    """Emite un voto en la sesión de votación activa."""
    if not sistema_votacion.tema_activo:
        return jsonify({"error": "No hay ninguna votación activa para votar"}), 400

    data = request.get_json()
    id_votante = data.get('id_votante') # Identificador externo del votante (e.g., DNI, email, etc.)
    id_candidato = data.get('id_candidato')

    if not id_votante or not id_candidato:
        return jsonify({"error": "Se requieren los campos 'id_votante' y 'id_candidato'"}), 400

    if sistema_votacion.emitir_voto_sesion(id_votante, str(id_candidato)): # Asegurar que id_candidato sea string
        return jsonify({"mensaje": f"Voto para el tema '{sistema_votacion.tema_activo}' registrado correctamente (pendiente de finalizar)"}), 200
    else:
        # El método interno imprime la causa (votante ya votó, candidato inválido, etc.)
        return jsonify({"error": "No se pudo registrar el voto (verifique los datos o si ya votó)"}), 400 # Bad request o Conflict 409

@app.route('/votacion/finalizar', methods=['POST'])
def finalizar_votacion_api():
    """Finaliza la votación activa, crea el bloque y lo añade a la cadena."""
    if not sistema_votacion.tema_activo:
        return jsonify({"error": "No hay ninguna votación activa para finalizar"}), 400

    if sistema_votacion.finalizar_votacion():
        return jsonify({"mensaje": f"Votación finalizada y bloque añadido a la blockchain."}), 200
    else:
        # El método interno imprime la causa (sin votos, error al añadir bloque)
        return jsonify({"error": "No se pudo finalizar la votación o añadir el bloque"}), 500

@app.route('/votacion/activa', methods=['GET'])
def obtener_votacion_activa_api():
    """Devuelve el estado de la votación activa, si existe."""
    estado = sistema_votacion.obtener_estado_votacion_activa()
    if estado:
        return jsonify(estado), 200
    else:
        return jsonify({"mensaje": "No hay ninguna votación activa en este momento"}), 404 # Not Found

# --- Rutas Anteriores (Modificadas o Mantenidas) ---

@app.route('/candidatos', methods=['GET', 'POST'])
def gestionar_candidatos_globales_api():
    """Gestiona candidatos globales (lista o registra uno nuevo)."""
    if request.method == 'GET':
        # Devuelve la lista global de candidatos
        return jsonify(sistema_votacion.candidatos_globales), 200
    elif request.method == 'POST':
        # Registra un nuevo candidato globalmente
        data = request.get_json()
        nombre = data.get('nombre')
        if not nombre:
            return jsonify({"error": "Se requiere el campo 'nombre'"}), 400

        id_candidato = sistema_votacion.registrar_candidato_global(nombre)
        if id_candidato:
            return jsonify({
                "mensaje": "Candidato registrado globalmente",
                "id_candidato": id_candidato,
                "nombre": nombre
                }), 201 # Created
        else:
            # El método interno ya imprime si existe o si hubo error
            return jsonify({"error": "No se pudo registrar el candidato global (posiblemente ya existe o error interno)"}), 409 # Conflict or 500

# --- Rutas de Consulta (Mantenidas/Adaptadas) ---

@app.route('/resultados', methods=['GET'])
def obtener_resultados_api():
    """Devuelve los resultados de la votación (global o por tema)."""
    tema = request.args.get('tema') # Permite filtrar por ?tema=NombreDelTema
    resultados_contados = sistema_votacion.contar_votos(tema_especifico=tema)

    # Convertir IDs de candidato a nombres para la respuesta JSON
    resultados_con_nombres = {
        sistema_votacion.candidatos_globales.get(id_c, f"ID Desconocido {id_c}"): votos
        for id_c, votos in resultados_contados.items()
    }

    # Indicar si hay una votación activa y si sus votos están incluidos
    estado_activo = sistema_votacion.obtener_estado_votacion_activa()
    info_adicional = {}
    if estado_activo and (tema is None or estado_activo["tema_activo"] == tema):
         info_adicional["votacion_activa"] = {
              "tema": estado_activo["tema_activo"],
              "votos_pendientes_incluidos": estado_activo["numero_votos_recibidos"]
         }


    return jsonify({
        "resultados": resultados_con_nombres,
        "info": info_adicional
        }), 200

@app.route('/cadena', methods=['GET'])
def obtener_cadena_api():
    """Devuelve la estructura completa de la blockchain."""
    cadena_serializada = [sistema_votacion._serializar_bloque(b) for b in sistema_votacion.cadena.cadena]
    return jsonify(cadena_serializada), 200

@app.route('/verificar', methods=['GET'])
def verificar_integridad_api():
    """Verifica la integridad de la blockchain."""
    es_valida = sistema_votacion.verificar_integridad_cadena()
    return jsonify({"integridad_valida": es_valida}), 200

# --- Ruta para la Interfaz Web (Sin cambios necesarios aquí) ---
@app.route('/')
def index():
    """Sirve la página principal del frontend."""
    # Verificar si el archivo index.html existe
    index_path = os.path.join(template_folder, 'index.html')
    if not os.path.isfile(index_path):
        return "Error: No se encuentra el archivo index.html en la carpeta de plantillas.", 404
    return render_template('index.html')

if __name__ == '__main__':
    # Asegúrate de que la IP y el puerto sean accesibles si es necesario
    # Usar 0.0.0.0 para permitir conexiones externas (útil en contenedores o VMs)
    app.run(host='0.0.0.0', port=5001, debug=True) # Puerto 5001 como en el original