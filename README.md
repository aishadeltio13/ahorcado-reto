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