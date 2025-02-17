from flask import Flask, render_template, request
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os

app = Flask(__name__)

# Estado de los apartamentos en memoria
ocupados = {}

# Definir la ubicación de los apartamentos según la imagen
posiciones = {
    1: (4.88, 3.2), 2: (-0.77, 2.7), 3: (-0.77, 2.1), 4: (-0.77, 1.5), 5: (-0.77, .88),
    6: (1.1, 2.7), 7: (1.1, 2.1), 8: (1.1, 1.5), 9: (1.1, .88),
    10: (4.88, 2.6), 11: (4.88, 2), 12: (4.88, 1.5), 13: (4.88, 1),
    18: (6.8, 3.2), 14: (6.8, 2.6), 15: (6.8, 2.1), 16: (6.8, 1.6), 17: (6.8, .97)
}

# Generar la imagen con el estado de los apartamentos
def generar_imagen():
    imagen = Image.open("static/edificio.png").transpose(Image.FLIP_TOP_BOTTOM)
    
    fig, ax = plt.subplots(figsize=(10, 7))
    ax.imshow(imagen, extent=[-1, 8, -1, 5])
    
    for num, (x, y) in posiciones.items():
        color = 'red' if ocupados.get(num, 0) == 1 else 'green'
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
    global ocupados

    if request.method == 'POST':
        ocupados_actualizados = {int(k): int(v) for k, v in request.form.to_dict().items()}
        ocupados.update(ocupados_actualizados)
        generar_imagen()

    generar_imagen()
    return render_template('index.html', ocupados=ocupados)

if __name__ == '__main__':
    app.run(debug=True)
