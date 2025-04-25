# gsi-voto_con_blockchain

Proyeto de laboratorio de la asignatura Gestión de Sistemas de Información

# Manual de usuario

Este manual describe cómo instalar y utilizar el sistema de votación basado en blockchain.

## Instalación y Ejecución

1.  **Clonar el repositorio (si aún no lo has hecho):**
    ```
    git clone <URL_DEL_REPOSITORIO>
    cd gsi-voto_con_blockchain
    ```

2.  **Crear un entorno virtual (recomendado):**
    ```
    python3 -m venv env
    source env/bin/activate  # En Linux/macOS
    # o
    # env\Scripts\activate  # En Windows
    ```

3.  **Instalar las dependencias:**
    ```
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**
    Navega al directorio `backend` y ejecuta el servidor Flask:
    ```
    cd backend
    python app.py
    ```
    La aplicación estará disponible en `http://localhost:5001` (o la dirección IP y puerto que muestre la consola).

## Uso de la Interfaz Web

Abre tu navegador web y ve a la dirección donde se está ejecutando la aplicación (`http://localhost:5001`). Verás la interfaz principal del sistema de votación.

### Gestión de Votación

Esta sección te permite administrar el ciclo de vida de una votación. Solo puede haber una votación activa a la vez.

1.  **Iniciar Nueva Votación:**
    *   Introduce un nombre o descripción para el **Tema de la votación** en el campo correspondiente.
    *   Haz clic en el botón **"Iniciar Votación"**.
    *   Si no hay otra votación activa, se iniciará una nueva sesión para el tema especificado. La interfaz se actualizará para mostrar el estado de la votación activa.

2.  **Añadir Candidatos:**
    *   Una vez iniciada una votación, aparecerá la sección para añadir candidatos.
    *   Introduce el **Nombre del Candidato** en el campo.
    *   Haz clic en **"Añadir Candidato"**.
    *   El candidato se añadirá a la lista de candidatos para la votación activa. Si el candidato no existía previamente en el sistema global, también se registrará globalmente.
    *   La lista de **"Candidatos Añadidos"** y el desplegable para emitir votos se actualizarán.

3.  **Emitir Voto:**
    *   Introduce tu **Identificación del Votante** (por ejemplo, DNI, número de estudiante, etc.) en el campo correspondiente. Este identificador se usará para asegurar que cada persona vote solo una vez por tema.
    *   Selecciona el **Candidato** al que deseas votar del menú desplegable.
    *   Haz clic en **"Emitir Voto"**.
    *   Tu voto se registrará temporalmente. Los contadores de **"Votos Recibidos"** y **"Votantes Participantes"** se actualizarán.

4.  **Finalizar Votación:**
    *   Cuando desees cerrar la votación activa y registrar permanentemente los votos emitidos:
    *   Haz clic en el botón **"Finalizar y Crear Bloque"**.
    *   Se te pedirá confirmación.
    *   Al confirmar, todos los votos emitidos para el tema activo se agruparán en un nuevo bloque que se añadirá a la blockchain.
    *   La sesión de votación activa terminará y la interfaz volverá al estado inicial, lista para iniciar una nueva votación.

### Consultas

Esta sección permite visualizar la información almacenada en la blockchain y el estado del sistema.

1.  **Resultados:**
    *   Para ver los resultados de todas las votaciones finalizadas (y la activa, si existe), haz clic en **"Ver Resultados"**.
    *   Si deseas ver los resultados solo para un tema específico, introduce el nombre del tema en el campo **"Filtrar por tema"** antes de hacer clic en el botón.
    *   Los resultados se mostrarán ordenados por número de votos. Si hay una votación activa, se indicará que sus votos (aún no en la blockchain) están incluidos en el recuento mostrado.

2.  **Cadena de Bloques:**
    *   Haz clic en **"Ver Cadena"** para mostrar la estructura completa de la blockchain en formato JSON. Cada bloque representa una votación finalizada (excepto el bloque Génesis inicial).
    *   Haz clic en **"Verificar Integridad"** para comprobar si la cadena de bloques ha sido manipulada desde que se cargó en memoria. Se mostrará un mensaje indicando si la cadena es válida o inválida.

3.  **Candidatos Globales:**
    *   Haz clic en **"Ver Candidatos Globales"** para mostrar una lista de todos los candidatos que han sido registrados en el sistema a lo largo de todas las votaciones.

### Mensajes de Estado

En la parte superior de la página, un área de mensajes mostrará información sobre las acciones realizadas, éxitos o errores.

