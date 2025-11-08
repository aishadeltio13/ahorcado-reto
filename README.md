# **Proyecto: Ahorcado (Versión de Prueba)**
## **Apuntes básicos**
En Python, sys.argv es una lista que contiene los argumentos que le pasas al programa desde la línea de comandos. El primer elemento (sys.argv[0]) es el nombre del script, y el segundo (sys.argv[1]) suele ser el primer argumento.

Ejemplo:

- python ahorcado.py palabras.txt

En ese caso, sys.argv sería igual a ['ahorcado.py', 'palabras.txt'].
### **Manejo de errores**
Si ejecuto el script sin pasarle ningún fichero (por ejemplo: python ahorcado.py), el programa muestra un mensaje de uso y se cierra limpiamente con sys.exit(1).
## **Desarrollo reciente: conexión con la API de la RAE**
Hoy estuve modificando el script del Ahorcado. El objetivo era bastante grande: dejar de leer un fichero local y, en su lugar, conectarme a una API de la RAE para pedir palabras aleatorias, procesarlas y guardarlas en la base de datos. Después me tocó pelearme un poco con Docker para que todo funcionara bien.
## **1. Estructura del código en Python**
El script pasó de ser un procesador batch (que leía un fichero y terminaba) a ser un servicio continuo que pide palabras sin parar. Tuve que reorganizar varias partes del código.
### **Funciones principales**
**get\_random\_word()** – Se conecta a la API de la RAE (https://rae-api.com/api/random) y maneja errores de red. Si la API falla o tarda demasiado, devuelve None para que el bucle principal reintente.

**normalizar\_palabra(palabra)** – Limpia la palabra quitando tildes y caracteres no válidos. Convierte todo a mayúsculas y solo deja letras A-Z.

**crear\_tabla(cursor)** – Comprueba que la tabla 'ahorcado' exista. Si no, la crea con CREATE TABLE IF NOT EXISTS.

**procesar\_una\_palabra(palabra\_limpia)** – Simula el juego del ahorcado para una palabra ya limpia. Devuelve una lista de tuplas con los estados del juego.

**guardar\_datos(cursor, registros)** – Guarda todos los registros de una palabra en la base de datos usando cursor.executemany(), lo que es más eficiente que varios INSERT.
### **Lógica principal**
En la parte principal del script (if \_\_name\_\_ == '\_\_main\_\_':), se establece la conexión con la base de datos, se crea la tabla si no existe y se inicia un bucle infinito. En cada ciclo, el script obtiene una palabra, la limpia, la procesa, guarda los resultados y espera 10 segundos antes de repetir. Todo está dentro de un try/except para poder detenerlo con Ctrl+C sin perder la conexión.
## **2. Docker: problemas y soluciones**
Error 1: service 'app' is not running

Intenté ejecutar 'docker compose -p ahorcado exec app python ahorcado.py', pero el contenedor no estaba corriendo. Aprendí que 'exec' solo funciona cuando el contenedor ya está activo. Lo correcto era usar 'docker compose -p ahorcado up'.

Error 2: ERROR: No matching distribution found for json

Vi este error en los logs al construir la imagen. Resulta que tenía 'json' en el requirements.txt, pero esa es una librería estándar de Python, no se instala con pip. Bastó con eliminar esa línea y reconstruir la imagen.
### **Paso final: reconstrucción de la imagen**
Después de corregir el requirements.txt, tuve que detener los servicios y reconstruir la imagen con '--build' para que Docker no usara la versión cacheada. Los comandos que usé fueron:

- docker compose -p ahorcado down
- docker compose -p ahorcado up -d --build
- docker compose -p ahorcado logs -f app

Finalmente, el servicio quedó corriendo correctamente: pide palabras nuevas desde la API, las limpia, simula el juego y guarda todo en la base de datos dentro del contenedor.
