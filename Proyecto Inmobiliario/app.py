from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os
import boto3

app = Flask(__name__)

# Configurar AWS DynamoDB
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')  # Cambia la región según tu configuración
table_name = "EstadoApartamentos"

# Verificar si la tabla existe, si no, crearla
def verificar_o_crear_tabla():
    existing_tables = boto3.client('dynamodb', region_name='us-east-1').list_tables()['TableNames']
    if table_name not in existing_tables:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'id_apartamento', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id_apartamento', 'AttributeType': 'N'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        print(f"Creando tabla {table_name}, espera un momento...")
        waiter = dynamodb.meta.client.get_waiter('table_exists')
        waiter.wait(TableName=table_name)
    return dynamodb.Table(table_name)

tabla = verificar_o_crear_tabla()

# Definir la ubicación de los apartamentos según la imagen
posiciones = {
    1: (4.88, 3.2), 2: (-0.77, 2.7), 3: (-0.77, 2.1), 4: (-0.77, 1.5), 5: (-0.77, .88),
    6: (1.1, 2.7), 7: (1.1, 2.1), 8: (1.1, 1.5), 9: (1.1, .88),
    10: (4.88, 2.6), 11: (4.88, 2), 12: (4.88, 1.5), 13: (4.88, 1),
    18: (6.8, 3.2), 14: (6.8, 2.6), 15: (6.8, 2.1), 16: (6.8, 1.6), 17: (6.8, .97)
}

# Obtener el estado actual de los apartamentos desde DynamoDB
def obtener_estado_apartamentos():
    response = tabla.scan()
    ocupados = {str(item['id_apartamento']): item['estado'] for item in response.get('Items', [])}
    return ocupados

# Guardar el estado de los apartamentos en DynamoDB
def guardar_estado_apartamentos(ocupados):
    with tabla.batch_writer() as batch:
        for id_apartamento, estado in ocupados.items():
            batch.put_item({
                'id_apartamento': int(id_apartamento),
                'estado': int(estado)
            })

# Generar la imagen con el estado de los apartamentos
def generar_imagen(ocupados):
    imagen = Image.open("static/edificio.png").transpose(Image.FLIP_TOP_BOTTOM)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(imagen, extent=[-1, 8, -1, 5])
    
    for num, (x, y) in posiciones.items():
        color = 'red' if ocupados.get(str(num), 0) == 1 else 'green'
        rect = plt.Rectangle((x + 0.2, y + 0.2), 0.6, 0.6, color=color, alpha=0.6, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + 0.5, y + 0.5, str(num), ha='center', va='center', fontsize=10, color='white')
    
    ax.set_xlim(-1, 8)
    ax.set_ylim(-1, 5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("Edificio - Estado de los Apartamentos", fontsize=14, fontweight='bold')
    plt.gca().invert_yaxis()
    
    if not os.path.exists("static"):
        os.makedirs("static")
    plt.savefig("static/edificio_estado.png")
    plt.close()

@app.route('/', methods=['GET', 'POST'])
def index():
    ocupados = obtener_estado_apartamentos()

    if request.method == 'POST':
        ocupados_actualizados = {k: int(v) for k, v in request.form.to_dict().items()}
        guardar_estado_apartamentos(ocupados_actualizados)
        ocupados = obtener_estado_apartamentos()
        generar_imagen(ocupados)

    generar_imagen(ocupados)
    return render_template('index.html', ocupados=ocupados)

if __name__ == '__main__':
    app.run(debug=True)
