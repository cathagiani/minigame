from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Juego: Estado global ---
ANCHO = 20
ALTO = 10
terreno = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
jugador_x = ANCHO // 2
jugador_y = ALTO // 2
camuflado = False
# Inicializa la imagen del jugador
imagen_jugador = "img/pagedoll.png"  # Imagen predeterminada
# Variable temporal para cambiar la imagen solo hasta que el jugador se mueva
imagen_bomba_desactivada = False


import random

# Nuevo: lista de bombas con sus coordenadas y estado
bombas = []

def inicializar_bombas():
    global bombas
    bombas = []
    cantidad = random.randint(5, 10)  # Entre 5 y 10 bombas
    while len(bombas) < cantidad:
        x = random.randint(0, ANCHO - 1)
        y = random.randint(0, ALTO - 1)
        # No poner bomba donde empieza el jugador
        if (x, y) != (jugador_x, jugador_y) and (x, y) not in [b[:2] for b in bombas]:
            bombas.append([x, y, False])  # [x, y, desactivada=False]



# Bombas en el mapa: cada bomba es un diccionario con x, y y su estado
bombas = [
    {'x': 5, 'y': 3, 'activa': True},
    {'x': 10, 'y': 7, 'activa': True},
]

def render_terreno():
    terreno_txt = '<table class="matriz">'
    for y in range(ALTO):
        terreno_txt += '<tr>'
        for x in range(ANCHO):
            terreno_txt += '<td>'
            if x == jugador_x and y == jugador_y:
                # Mostrar la imagen del jugador dependiendo del estado
                terreno_txt += f'<img src="/static/{ imagen_jugador if not imagen_bomba_desactivada else "img/jugador_bomba.png" }" class="jugador">'
            elif any(bx == x and by == y and not desactivada for bx, by, desactivada in bombas):
                terreno_txt += '<img src="/static/img/bomba.png" class="bomba">'  # Bomba activa
            elif any(bx == x and by == y and desactivada for bx, by, desactivada in bombas):
                terreno_txt += '<img src="/static/img/bomba_off.png" class="bomba">'  # Bomba desactivada
            else:
                terreno_txt += '.'
            terreno_txt += '</td>'
        terreno_txt += '</tr>'
    terreno_txt += '</table>'
    return terreno_txt


def mover_jugador(direccion):
    global jugador_x, jugador_y, camuflado, imagen_jugador, imagen_bomba_desactivada
    mensaje = ""

    # Revertir la imagen después de un movimiento
    if imagen_bomba_desactivada:
        imagen_jugador = "img/pagedoll.png" if not camuflado else "img/borgir.png"
        imagen_bomba_desactivada = False  # Restablece la bandera después de mover

    # Mover al jugador según la dirección
    if direccion == 'W' and jugador_y > 0:
        jugador_y -= 1
    elif direccion == 'S' and jugador_y < ALTO - 1:
        jugador_y += 1
    elif direccion == 'A' and jugador_x > 0:
        jugador_x -= 1
    elif direccion == 'D' and jugador_x < ANCHO - 1:
        jugador_x += 1
    elif direccion == 'Q':
        camuflado = not camuflado
        mensaje = "Te camuflaste!" if camuflado else "Dejaste de camuflarte!"
    
    # Revisa si el jugador está encima de una bomba
    for bomba in bombas:
        bx, by, desactivada = bomba
        if bx == jugador_x and by == jugador_y and not desactivada:
            if not camuflado:
                bomba[2] = True  # Desactivar la bomba
                mensaje = "¡Desactivaste una bomba!"
                imagen_jugador = "img/jugador_bomba.png"  # Cambia la imagen del jugador cuando desactiva una bomba
                imagen_bomba_desactivada = True  # Marca que la imagen se ha cambiado por desactivar una bomba
            else:
                mensaje = "¡No puedes desactivar bomba mientras estás camuflado!"
    
    # Ganar si todas las bombas están desactivadas
    if all(desactivada for _, _, desactivada in bombas):
        mensaje = "¡Ganaste! Todas las bombas desactivadas."
    
    return mensaje



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mover', methods=['POST'])
def mover():
    global jugador_x, jugador_y, camuflado
    data = request.json
    direccion = data.get('direccion', '')

    # Si es inicio de partida
    if direccion == '':
        jugador_x = ANCHO // 2
        jugador_y = ALTO // 2
        camuflado = False
        inicializar_bombas()

    mensaje = mover_jugador(direccion.upper())
    return jsonify({
        'terreno': render_terreno(),
        'mensaje': mensaje
    })


if __name__ == '__main__':
    app.run(debug=True)