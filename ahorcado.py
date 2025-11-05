import string
import os
import sys
import psycopg
import datetime  

# Conexion base de datos
try:
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Error: La variable de entorno DATABASE_URL no está definida.")
        sys.exit(1)
        
    connection = psycopg.connect(url)
    cur = connection.cursor()
    print("BD conectada con éxito")
except Exception as e:
    print(f"Error al conectar a la BD: {e}")
    sys.exit(1) # Si no hay BD, salimos.


ABECEDARIO = string.ascii_uppercase  # "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

def crear_tabla_log_intentos(cursor):
    """
    Crea la tabla 'log_intentos_ahorcado' si no existe.
    Esta tabla NO tiene 'palabra' como única, para permitir
    múltiples registros por palabra.
    """
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS log_intentos_ahorcADO (
            id SERIAL PRIMARY KEY,
            palabra VARCHAR(255) NOT NULL,
            letras_acertadas VARCHAR(100),
            letras_fallidas VARCHAR(100),
            intentos INTEGER NOT NULL,
            tiempo TIMESTAMP NOT NULL
        );
        """)
        connection.commit() # commit de la creación de la tabla
        print("Tabla 'log_intentos_ahorcado' creada.")
    except Exception as e:
        print(f"Error al crear la tabla: {e}")
        connection.rollback() # revertimos si hay error


def procesar_palabras_y_guardar_log(fichero_palabras, cursor):
    """
    Procesa el fichero de palabras y guarda CADA INTENTO
    en la base de datos.
    """
    
    # Comprobar si el fichero existe
    if not os.path.exists(fichero_palabras):
        print(f"Error: El fichero '{fichero_palabras}' no se ha encontrado.")
        return

    # SQL para insertar cada intento (log)
    sql_insert_log = """
    INSERT INTO log_intentos_ahorcado 
        (palabra, letras_acertadas, letras_fallidas, intentos, tiempo)
    VALUES (%s, %s, %s, %s, %s);
    """

    try:
        with open(fichero_palabras, 'r', encoding='utf-8') as fichero:
            
            for linea in fichero:
                palabra = linea.strip().upper()
                
                # Si la línea estaba vacía, la saltamos
                if not palabra:
                    continue
                
                print(f"--- Procesando palabra: {palabra} ---")
                
                letras_objetivo = set(palabra) # Las letras que contiene la palabra
                
                # Variables para esta palabra
                intentos = 0
                letras_acertadas = set()
                letras_fallidas = set() 
                
                # Recorremos el abecedario letra por letra
                for letra_del_abecedario in ABECEDARIO:
                    # 1. Sumamos un intento
                    intentos += 1
                    
                    # 2. Comparamos la letra
                    if letra_del_abecedario in letras_objetivo:
                        letras_acertadas.add(letra_del_abecedario)
                    else:
                        letras_fallidas.add(letra_del_abecedario)
                    
                    # 3. Obtenemos el tiempo actual
                    tiempo_actual = datetime.datetime.now()
                    
                    # 4. Convertimos los sets a strings ordenados (para la BD)
                    str_acertadas = "".join(sorted(letras_acertadas))
                    str_fallidas = "".join(sorted(letras_fallidas))
                    
                    # 5. Guardamos ESTE intento en la BD
                    try:
                        cursor.execute(sql_insert_log, (
                            palabra,
                            str_acertadas,
                            str_fallidas,
                            intentos,
                            tiempo_actual
                        ))
                        # Imprimimos el log para que veas el progreso
                        print(f"  -> Intento {intentos}: Letra '{letra_del_abecedario}' | Acertadas: '{str_acertadas}' | Fallidas: '{str_fallidas}'")
                        
                    except Exception as e:
                        print(f"Error al insertar el intento {intentos} para '{palabra}': {e}")
                        connection.rollback() # Revertimos este intento fallido
                    
                    # 6. Comprobar si ya hemos encontrado todas las letras
                    if letras_acertadas == letras_objetivo:
                        print(f"Palabra '{palabra}' completada en {intentos} intentos.")
                        break # Salimos del bucle del abecedario
                
                # Hacemos commit de todos los intentos de ESTA palabra
                connection.commit()

        print("\n--- Proceso completado ---")

    except Exception as e:
        print(f"Ha ocurrido un error leyendo el fichero: {e}")
        return None


if __name__ == "__main__":
    
    if len(sys.argv) < 2:
        print("Uso: python ahorcado.py <nombre_del_fichero>")
        sys.exit(1)

    # --- 1. Aseguramos que la tabla de logs exista ---
    crear_tabla_log_intentos(cur)

    # --- 2. Procesamos el fichero y guardamos el log ---
    fichero_palabras = sys.argv[1]
    procesar_palabras_y_guardar_log(fichero_palabras, cur)
    
    # --- 3. Cerramos la conexión ---
    print("Cerrando conexión con la BD.")
    cur.close()
    connection.close()
            


