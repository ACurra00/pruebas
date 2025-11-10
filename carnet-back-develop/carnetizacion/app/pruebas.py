import psycopg2


DB_NAME = "carnetizacion"
DB_USER = "postgres"
DB_PASS = "postgres"
DB_HOST = "LOCALHOST"
DB_PORT = "5432"

try:
    connection = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    #print("Conexión exitosa")

    
except Exception as e:
    #print(f"Error al conectar: {e}")
    a = 1+0


cursor = connection.cursor()

# Ejemplo de consulta
try:
    cursor.execute("SELECT * FROM person;")
    rows = cursor.fetchall()
    for row in rows:
        #print(row)
        b=1
except Exception as e:
    #print(f"Error al ejecutar la consulta: {e}")
    a = 1
finally:
    cursor.close()