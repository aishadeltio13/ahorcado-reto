# ahorcado-prueba

apuntes:

sys.argv es una lista que contiene los argumentos que le pasas al programa.

sys.argv[0] → nombre del script (ahorcado.py)

sys.argv[1] → el primer argumento después del script (en este caso, palabras.txt)

Ejemplo:

python ahorcado.py palabras.txt


Entonces:

sys.argv == ['ahorcado.py', 'palabras.txt']

🛡️ Extra: manejo de errores

Si ejecutas el script sin pasarle ningún fichero:

python ahorcado.py


El programa mostrará:

Uso: python ahorcado.py <nombre_del_fichero>


y se cerrará sin error gracias a:

sys.exit(1)


Hoy estuve modificando el script del Ahorcado. El objetivo era grande: dejar de leer un fichero local y, en su lugar, conectarme a una API de la RAE para pedir palabras aleatorias sin parar, procesarlas y guardarlas en la base de datos. Luego, me peleé un poco con Docker para ponerlo todo en marcha.

🐍 1. Estructura del Código en Python
El script pasó de ser un procesador "batch" (leía un fichero y terminaba) a ser un servicio continuo (un bucle infinito que pide palabras). Tuve que reorganizarlo bastante.

Funciones Principales:
get_random_word():

Es la función nueva que se conecta a la API (https://rae-api.com/api/random).

Usa requests.get() y maneja errores de red (RequestException). Si la API falla o tarda mucho, devuelve None y el bucle principal sabe que debe reintentar.

normalizar_palabra(palabra):

¡Esta función es crucial! La API devuelve palabras "sucias" para mi simulación (ej. "¡Pingüino!", "corazón").

La simulación del ahorcado solo funciona con las letras A-Z (mi ABECEDARIO).

Esta función usa unicodedata para quitar tildes ("corazón" -> "corazon") y luego filtra todo lo que no sea una letra A-Z ("¡Pingüino!" -> "PINGUINO").

Si una palabra no tiene letras válidas (ej. "¡¡!!"), devuelve una cadena vacía.

crear_tabla(cursor):

La misma de antes. Solo se asegura de que la tabla ahorcado exista con un CREATE TABLE IF NOT EXISTS.

procesar_una_palabra(palabra_limpia):

El corazón de la simulación. Antes esto procesaba una lista de palabras, ahora procesa una sola.

Recibe la palabra ya limpia (ej. "CASA").

Itera por el ABECEDARIO (A, B, C...) simulando los intentos.

En cada intento (cada letra del abecedario), guarda el estado completo del juego (palabra, acertadas, fallidas, intentos) en una lista.

Si la palabra es "CASA", esta función devuelve una lista de 4 registros (uno por la A, B, C, D... hasta la S, que sería la última letra que necesita).

Importante: Devuelve una lista de tuplas, lista para el executemany.

guardar_datos(cursor, registros):

Es una función de ayuda simple.

Usa cursor.executemany() para guardar todos los pasos de la simulación de una palabra (la lista que devuelve procesar_una_palabra) en la base de datos de golpe. Es mucho más eficiente que hacer un INSERT por cada paso.

Lógica Principal (if __name__ == "__main__":)
Aquí es donde se orquesta todo:

Conexión Persistente: Abre una única conexión a la base de datos (psycopg.connect) que se mantiene viva durante todo el proceso.

Crear Tabla: Llama a crear_tabla() una sola vez al arrancar el script.

Bucle Infinito: Entra en un while True:.

Ciclo de Juego (dentro del bucle):

Obtener: Llama a get_random_word(). Si falla, imprime un error y el bucle vuelve a empezar (esperando 10 seg).

Limpiar: Llama a normalizar_palabra(). Si la palabra queda vacía, se la salta.

Procesar: Llama a procesar_una_palabra().

Guardar: Llama a guardar_datos() con los resultados del procesamiento.

Commit: ¡Clave! Llama a conn.commit(). Esto guarda los cambios de esa palabra en la BD de forma permanente. Si el script se cae después, esa palabra ya está salvada.

Esperar: Llama a time.sleep(10) para cumplir el requisito de esperar 10 segundos antes de pedir la siguiente palabra.

Cierre Limpio: Todo está envuelto en un try...except KeyboardInterrupt para que, si pulso Ctrl+C, el script salga del bucle y el finally cierre la conexión a la base de datos correctamente.

🐳 2. Problemas y Soluciones con Docker
Aquí es donde me atasqué un poco al intentar ponerlo en marcha.

Error 1: service "app" is not running
Qué hice: Intenté ejecutar docker compose -p ahorcado exec app python ahorcado.py.

Problema: exec sirve para ejecutar un comando en un contenedor que ya está corriendo. Mi contenedor app no estaba corriendo, intentaba usar exec para iniciarlo.

Lección:

docker compose **up**: Inicia los servicios definidos en el docker-compose.yml.

docker compose **exec**: Se usa para "meterse" o ejecutar algo más en un contenedor activo.

Solución: Tenía que usar docker compose -p ahorcado up. El command: python ahorcado.py en mi docker-compose.yml (o en el Dockerfile) se encarga de lanzar el script automáticamente cuando el contenedor arranca.

Error 2: ERROR: No matching distribution found for json
Qué hice: Después de arreglar lo anterior y lanzar docker compose up, vi en los logs (docker compose logs -f app) que la construcción fallaba.

Problema: El log de pip install -r requirements.txt decía que no encontraba el paquete json.

Lección: json es una librería estándar de Python (viene incluida por defecto, como os o string). No se instala con pip.

Solución:

Abrir mi archivo requirements.txt.

Borrar la línea que decía json.

Paso Final (Crucial): Reconstruir la Imagen
Después de editar requirements.txt, no basta con hacer docker compose up otra vez. Docker usaría la imagen "cacheada" que todavía tiene el error.

Flujo correcto para arreglarlo:

Parar todo: docker compose -p ahorcado down

Reconstruir la imagen (con el requirements.txt corregido) y levantarla: docker compose -p ahorcado up -d --build (el flag --build es la clave).

Verificar que ahora sí funciona: docker compose -p ahorcado logs -f app