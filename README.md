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
