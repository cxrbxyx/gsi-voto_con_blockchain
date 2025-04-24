const API_BASE_URL = ''; // Usar rutas relativas si Flask sirve el frontend

// --- Funciones Auxiliares ---
async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        const contentType = response.headers.get("content-type");
        let data;

        if (contentType && contentType.indexOf("application/json") !== -1) {
            data = await response.json();
        } else {
            // Si no es JSON, intenta obtener texto (útil para errores HTML)
            data = await response.text();
        }

        if (!response.ok) {
            // Intenta obtener el mensaje de error del JSON si existe, si no usa el texto
            const errorMessage = (typeof data === 'object' && data?.error)
                                 ? data.error
                                 : (typeof data === 'string' ? data : `HTTP error! status: ${response.status}`);
            throw new Error(errorMessage);
        }

        // Si la respuesta es OK pero no es JSON (raro pero posible), devuelve un objeto indicándolo
        if (typeof data === 'string') {
             return { success: true, message: data }; // O ajusta según necesidad
        }

        return data; // Devuelve el objeto JSON parseado
    } catch (error) {
        console.error('Error en fetch:', error);
        mostrarMensaje(`Error: ${error.message}`, 'error');
        throw error; // Re-lanza el error
    }
}

function mostrarMensaje(mensaje, tipo = 'info') {
    const statusDiv = document.getElementById('status-messages');
    if (!statusDiv) {
        console.error("Elemento 'status-messages' no encontrado.");
        alert(`${tipo.toUpperCase()}: ${mensaje}`); // Fallback a alert
        return;
    }
    statusDiv.textContent = mensaje;
    statusDiv.className = `status ${tipo}`;
    // Opcional: ocultar el mensaje después de unos segundos
    setTimeout(() => {
        if (statusDiv.textContent === mensaje) { // Solo limpia si el mensaje no ha cambiado
            statusDiv.textContent = '';
            statusDiv.className = 'status';
        }
    }, 7000); // Aumentado a 7 segundos
}

function actualizarSelect(selectId, data, valueField, textField, placeholder, clearFirst = true) {
    const select = document.getElementById(selectId);
    if (!select) return;
    if (clearFirst) {
        select.innerHTML = ''; // Limpiar opciones existentes
    }
    if (placeholder) {
        const option = document.createElement('option');
        option.value = "";
        option.textContent = placeholder;
        option.disabled = true;
        option.selected = true;
        select.appendChild(option);
    }
    // Asegurarse de que data es un objeto iterable
    if (typeof data === 'object' && data !== null) {
        for (const id in data) {
            const option = document.createElement('option');
            option.value = data[id][valueField] !== undefined ? data[id][valueField] : id; // Usar ID como valor si no hay campo específico
            // Si data[id] es un objeto, usa el campo de texto, si no, usa el valor directamente
            option.textContent = typeof data[id] === 'object' ? data[id][textField] : data[id];
            select.appendChild(option);
        }
    } else {
        console.warn(`Datos inválidos para actualizar select '${selectId}':`, data);
    }
}

function actualizarLista(listId, data, displayField = null, keyIsId = true) {
    const list = document.getElementById(listId);
    if (!list) return;
    list.innerHTML = ''; // Limpiar lista
    if (typeof data === 'object' && data !== null) {
        for (const key in data) {
            const li = document.createElement('li');
            const id = keyIsId ? key : data[key].id; // Asume que la clave es el ID o hay un campo 'id'
            const value = data[key];
            let textContent = `ID: ${id}`;

            if (typeof value === 'object' && displayField && value[displayField]) {
                textContent += ` - Nombre: ${value[displayField]}`;
            } else if (typeof value !== 'object') {
                textContent += ` - Nombre: ${value}`;
            } else {
                 textContent += ` - (Sin nombre especificado)`;
            }
            li.textContent = textContent;
            list.appendChild(li);
        }
         if (Object.keys(data).length === 0) {
             const li = document.createElement('li');
             li.textContent = "(Lista vacía)";
             li.style.fontStyle = 'italic';
             list.appendChild(li);
         }
    } else {
         const li = document.createElement('li');
         li.textContent = "(No hay datos disponibles)";
         li.style.fontStyle = 'italic';
         list.appendChild(li);
    }
}

// --- Gestión del Estado de la Interfaz ---
function actualizarUIEstadoVotacion(estado) {
    const iniciarSection = document.getElementById('iniciar-votacion-section');
    const estadoSection = document.getElementById('estado-votacion-activa');
    const agregarCandidatoSection = document.getElementById('agregar-candidato-section');
    const emitirVotoSection = document.getElementById('emitir-voto-section');
    const finalizarSection = document.getElementById('finalizar-votacion-section');
    const temaActivoSpans = document.querySelectorAll('.tema-activo-ref'); // Para actualizar el tema en varios lugares

    if (estado && estado.tema_activo) {
        // Hay una votación activa
        iniciarSection.style.display = 'none';
        estadoSection.style.display = 'block';
        agregarCandidatoSection.style.display = 'block';
        emitirVotoSection.style.display = 'block';
        finalizarSection.style.display = 'block';

        document.getElementById('tema-activo-span').textContent = estado.tema_activo;
        temaActivoSpans.forEach(span => span.textContent = estado.tema_activo); // Actualizar referencias al tema
        document.getElementById('votos-recibidos-span').textContent = estado.numero_votos_recibidos || 0;
        document.getElementById('votantes-participantes-span').textContent = estado.numero_votantes_participantes || 0;

        // Actualizar lista de candidatos activos y el select para votar
        actualizarLista('candidatos-activos-lista', estado.candidatos || {}, null, true); // key es ID, value es nombre
        actualizarSelect('select-candidato-activo', estado.candidatos || {}, 'id', 'nombre', 'Selecciona un candidato', true); // key es ID, value es nombre

    } else {
        // No hay votación activa
        iniciarSection.style.display = 'block';
        estadoSection.style.display = 'none';
        agregarCandidatoSection.style.display = 'none';
        emitirVotoSection.style.display = 'none';
        finalizarSection.style.display = 'none';
    }
}

// --- Carga de Datos Inicial y Estado ---
async function obtenerEstadoVotacionActiva() {
    try {
        const estado = await fetchData(`${API_BASE_URL}/votacion/activa`);
        actualizarUIEstadoVotacion(estado);
        return estado; // Devuelve el estado por si se necesita
    } catch (error) {
        // Si da 404 (Not Found), significa que no hay votación activa
        if (error.message.includes('404')) {
            actualizarUIEstadoVotacion(null); // Asegura que la UI muestre el estado "sin votación"
        } else {
            mostrarMensaje('Error al obtener el estado de la votación activa.', 'error');
        }
        return null;
    }
}

async function cargarCandidatosGlobales() {
    try {
        const candidatos = await fetchData(`${API_BASE_URL}/candidatos`);
        actualizarLista('lista-candidatos-globales', candidatos, null, true); // key es ID, value es nombre
    } catch (error) {
        mostrarMensaje('Error al cargar la lista de candidatos globales.', 'error');
    }
}

// --- Acciones del Usuario (Nuevas y Modificadas) ---

async function iniciarVotacion() {
    const tema = document.getElementById('tema-votacion-input').value;
    if (!tema) {
        mostrarMensaje('Por favor, introduce un tema para la votación.', 'error');
        return;
    }
    try {
        const result = await fetchData(`${API_BASE_URL}/votacion/iniciar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tema: tema })
        });
        mostrarMensaje(result.mensaje || `Votación para '${tema}' iniciada.`, 'success');
        document.getElementById('tema-votacion-input').value = ''; // Limpiar input
        await obtenerEstadoVotacionActiva(); // Actualizar UI
    } catch (error) {
        // El error ya se muestra en fetchData
    }
}

async function agregarCandidatoAVotacion() {
    const nombre = document.getElementById('nombre-candidato-activo').value;
    if (!nombre) {
        mostrarMensaje('Por favor, introduce un nombre para el candidato.', 'error');
        return;
    }
    try {
        const result = await fetchData(`${API_BASE_URL}/votacion/candidato`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ nombre: nombre })
        });
        mostrarMensaje(result.mensaje || `Candidato '${nombre}' añadido/confirmado.`, 'success');
        document.getElementById('nombre-candidato-activo').value = ''; // Limpiar input
        await obtenerEstadoVotacionActiva(); // Recargar estado para actualizar listas
        await cargarCandidatosGlobales(); // Actualizar lista global por si era nuevo
    } catch (error) {
        // El error ya se muestra en fetchData
    }
}

async function emitirVotoSesion() {
    const idVotante = document.getElementById('id-votante-input').value;
    const idCandidato = document.getElementById('select-candidato-activo').value;

    if (!idVotante) {
        mostrarMensaje('Por favor, introduce tu identificación.', 'error');
        return;
    }
     if (!idCandidato) {
        mostrarMensaje('Por favor, selecciona un candidato.', 'error');
        return;
    }

    try {
        const result = await fetchData(`${API_BASE_URL}/votacion/votar`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id_votante: idVotante,
                id_candidato: idCandidato
            })
        });
        mostrarMensaje(result.mensaje || 'Voto emitido correctamente (pendiente de finalizar).', 'success');
        document.getElementById('id-votante-input').value = ''; // Limpiar input votante
        // No limpiamos el candidato seleccionado por si votan varias personas seguidas
        await obtenerEstadoVotacionActiva(); // Actualizar contadores de votos/votantes
    } catch (error) {
       // El error ya se muestra en fetchData
    }
}

async function finalizarVotacion() {
    if (!confirm('¿Estás seguro de que quieres finalizar la votación actual y crear el bloque?')) {
        return;
    }
    try {
        const result = await fetchData(`${API_BASE_URL}/votacion/finalizar`, {
            method: 'POST'
        });
        mostrarMensaje(result.mensaje || 'Votación finalizada y bloque creado.', 'success');
        await obtenerEstadoVotacionActiva(); // La UI debería volver al estado inicial
        await obtenerCadena(); // Actualizar la visualización de la cadena
        await obtenerResultados(); // Actualizar resultados
    } catch (error) {
        // El error ya se muestra en fetchData
    }
}

// --- Funciones de Consulta (Adaptadas) ---

async function obtenerResultados() {
    const temaFiltro = document.getElementById('tema-resultados-filtro').value;
    const url = new URL(`${API_BASE_URL}/resultados`, window.location.origin);
    if (temaFiltro) {
        url.searchParams.append('tema', temaFiltro);
    }

    try {
        const data = await fetchData(url.toString());
        const { resultados, info } = data;
        const resultadosDiv = document.getElementById('resultados');
        const infoDiv = document.getElementById('info-resultados-adicional');
        resultadosDiv.innerHTML = ''; // Limpiar
        infoDiv.innerHTML = ''; // Limpiar info adicional

        if (Object.keys(resultados).length > 0) {
            const ul = document.createElement('ul');
            // Ordenar resultados por votos (descendente)
            const sortedResultados = Object.entries(resultados).sort(([,a],[,b]) => b-a);

            for (const [nombreCandidato, votos] of sortedResultados) {
                const li = document.createElement('li');
                li.textContent = `${nombreCandidato}: ${votos} votos`;
                ul.appendChild(li);
            }
            resultadosDiv.appendChild(ul);
        } else {
            resultadosDiv.textContent = 'No hay votos registrados para mostrar' + (temaFiltro ? ` para el tema '${temaFiltro}'.` : '.');
        }

        // Mostrar información adicional (votos pendientes incluidos)
        if (info && info.votacion_activa) {
             infoDiv.innerHTML = `<p><small><i>(Incluye ${info.votacion_activa.votos_pendientes_incluidos} votos pendientes de la votación activa '${info.votacion_activa.tema}')</i></small></p>`;
        }

    } catch (error) {
        document.getElementById('resultados').textContent = 'Error al cargar resultados.';
        document.getElementById('info-resultados-adicional').innerHTML = '';
    }
}

async function obtenerCadena() {
    try {
        const cadena = await fetchData(`${API_BASE_URL}/cadena`);
        const cadenaPre = document.getElementById('cadena-bloques-pre');
        if (cadena && cadena.length > 0) {
            // Opcional: Mapear IDs de candidatos a nombres si la API no lo hace
            // (Asumiendo que la API ya devuelve nombres o que tenemos la lista global)
            cadenaPre.textContent = JSON.stringify(cadena, null, 2);
        } else {
            cadenaPre.textContent = 'La cadena está vacía o no se pudo cargar.';
        }
    } catch (error) {
        document.getElementById('cadena-bloques-pre').textContent = 'Error al cargar la cadena.';
    }
}

async function verificarIntegridad() {
    try {
        const result = await fetchData(`${API_BASE_URL}/verificar`); // Endpoint cambiado
        if (result.integridad_valida) {
            mostrarMensaje('La integridad de la cadena de bloques es VÁLIDA.', 'success');
        } else {
            mostrarMensaje('¡ALERTA! La integridad de la cadena de bloques es INVÁLIDA.', 'error');
        }
    } catch (error) {
        // El error ya se muestra en fetchData
    }
}

// --- Funciones Eliminadas ---
// registrarVotante()
// cargarVotantes()
// resetearVotantes()
// crearBloque()
// La funcionalidad de registrar candidato globalmente se hace ahora al añadirlo a una votación si no existe.
// Se podría añadir un botón específico si se desea registrar candidatos sin iniciar votación.

// --- Carga Inicial ---
document.addEventListener('DOMContentLoaded', () => {
    obtenerEstadoVotacionActiva(); // Determina qué secciones mostrar
    cargarCandidatosGlobales(); // Carga la lista de candidatos globales
    obtenerCadena(); // Muestra la cadena inicial
    obtenerResultados(); // Muestra los resultados iniciales
});