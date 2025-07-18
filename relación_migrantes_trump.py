

pip install mysql-connector-python

import mysql.connector
import requests
import json
import mysql.connector
import matplotlib.pyplot as plt



# URL para la consulta de metadatos de los indicadores
url = "https://www.inegi.org.mx/app/api/indicadores/desarrolladores/jsonxml/INDICATOR/6200240327/es/0700/false/BISE/2.0/e01ac2b5-b0f5-1c27-e46e-d606b96c5b5a?"

# Realizar la solicitud GET a la API
response = requests.get(url)

# Verificar si la solicitud fue exitosa
if response.status_code == 200:
    # Convertir la respuesta a formato JSON
    data = response.json()


    # Extraer las observaciones
    series = data.get("Series", [])
    if series:
        observations = series[0].get("OBSERVATIONS", [])
        # Listas para los años y valores
        years = []
        percentages = []

        for obs in observations:
            year = obs.get("TIME_PERIOD")
            percentage = obs.get("OBS_VALUE")
            if year and percentage:
                years.append(year)
                percentages.append(float(percentage))

        # Imprimir los datos extraídos
        print("Años:", years)
        print("Porcentajes:", percentages)
    else:
        print("No se encontraron datos en la respuesta.")
else:
    print(f"Error al obtener los datos: {response.status_code}")

# Conexión a la base de datos
connection = mysql.connector.connect(
    host="sql3.freemysqlhosting.net",  # Cambia esto si tu servidor tiene otra configuración
    user="sql3738731",  # Tu usuario de MySQL
    password="tEK9WeRN35",  # Tu contraseña de MySQL
    database="sql3738731"  # Base de datos que creaste
)

cursor = connection.cursor()

# Insertar los datos en la tabla
try:
    for year, percentage in zip(years, percentages):
        cursor.execute(
            "INSERT INTO emigration_data (year, percentage) VALUES (%s, %s) ON DUPLICATE KEY UPDATE percentage = %s",
            (year, percentage, percentage)
        )
    # Confirmar cambios
    connection.commit()
    print("Datos insertados correctamente.")
except Exception as e:
    print(f"Error al insertar los datos: {e}")
    connection.rollback()
finally:
    cursor.close()
    connection.close()

#GRAFICA BASE DE DATOS INEGI
years = ['2014', '2018', '2023']
percentages = [86.3, 84.8, 87.9]

# Crear el gráfico de barras
plt.figure(figsize=(8, 6))  # Ajustar tamaño de la figura
plt.bar(years, percentages, color=['skyblue', 'lightcoral', 'lightgreen'])
plt.xlabel("Año")
plt.ylabel("Porcentaje")
plt.title("Porcentajes de migración mexicana hacia Estados Unidos por parte del INEGI")

# Ponemos porcentajes encima
for i, percentage in enumerate(percentages):
    plt.text(i, percentage + 0.5, f"{percentage:.1f}%", ha='center', va='bottom')

plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.show()


# Establecemos conexión con la base de datos "sbo_encounters"
connection = mysql.connector.connect(
    host="sql3.freemysqlhosting.net",
    user="sql3738731",
    password="tEK9WeRN35",
    database="sql3738731",
    port=3306
)

# Crear un cursor para ejecutar las consultas
cursor = connection.cursor()

# Query para obtener los datos mensuales totales
query_total = """
SELECT `month`,
       SUM(`Encounter_count`) AS total_migrants
FROM sbo_encounters
GROUP BY `month`
ORDER BY FIELD(`month`, 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC');
"""

# Nuevo query para obtener datos de migrantes mexicanos
query_mexico = """
SELECT month,
       SUM(Encounter_count) AS total_apprehensions
FROM sbo_encounters
WHERE component = 'U.S'
  AND citizenship_grouping = 'Mexico'
  AND Encounter_type = 'Apprehensions'
GROUP BY month
ORDER BY FIELD(month, 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC');
"""

# Ejecutar la consulta para el total de migrantes
cursor.execute(query_total)
# Obtener los resultados en una lista de tuplas
resultado_total = cursor.fetchall()
print(resultado_total)


# Ejecutar la consulta para los migrantes mexicanos
cursor.execute(query_mexico)
# Obtener los resultados en una lista de tuplas
resultado_mexico = cursor.fetchall()

# Cerrar la conexión con la base de datos
cursor.close()
connection.close()

# Preparar los datos para las gráficas
months = [row[0] for row in resultado_total]  # Extraer los meses
total_migrantes = [row[1] for row in resultado_total]  # Extraer el total de migrantes
mexico_migrantes = [row[1] for row in resultado_mexico]  # Extraer el total de migrantes mexicanos

# Crear subgráficas para comparar
fig, ax = plt.subplots(2, 1, figsize=(12, 10))

# Gráfica para todos los migrantes
ax[0].bar(months, total_migrantes, color='skyblue')
ax[0].set_title('Total de Migrantes Expulsados', fontsize=14)
ax[0].set_xlabel('Mes', fontsize=12)
ax[0].set_ylabel('Número de Migrantes', fontsize=12)

# Gráfica para migrantes mexicanos
ax[1].bar(months, mexico_migrantes, color='lightcoral')
ax[1].set_title('Total de Migrantes Mexicanos Expulsados', fontsize=14)
ax[1].set_xlabel('Mes', fontsize=12)
ax[1].set_ylabel('Número de Migrantes Mexicanos', fontsize=12)

plt.tight_layout()
plt.show()