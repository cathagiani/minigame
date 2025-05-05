from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# --- Juego: Estado global ---
ANCHO = 20
ALTO = 10
terreno = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
jugador_x = ANCHO // 2
jugador_y = ALTO // 2
camuflado = False
imagen_jugador = "img/woofzn.png"
imagen_bonshot_besado = False

# Lista de bonshots
bonshots = []

def inicializar_bonshots():
    global bonshots
    bonshots = []
    cantidad = random.randint(5, 10)
    while len(bonshots) < cantidad:
        x = random.randint(0, ANCHO - 1)
        y = random.randint(0, ALTO - 1)
        if (x, y) != (jugador_x, jugador_y) and (x, y) not in [b[:2] for b in bonshots]:
            bonshots.append([x, y, False])  # [x, y, besado=False]

def render_terreno():
    terreno_txt = '<table class="matriz">'
    for y in range(ALTO):
        terreno_txt += '<tr>'
        for x in range(ANCHO):
            terreno_txt += '<td>'
            if x == jugador_x and y == jugador_y:
                terreno_txt += f'<img src="/static/{ imagen_jugador if not imagen_bonshot_besado else "img/kissy.png" }" class="jugador">'
            elif any(bx == x and by == y and not besado for bx, by, besado in bonshots):
                terreno_txt += '<img src="/static/img/bonshot.png" class="bonshot">'  # Bonshot activo
            elif any(bx == x and by == y and besado for bx, by, besado in bonshots):
                terreno_txt += '<img src="/static/img/kissedbonshot.png" class="bonshot">'  # Bonshot besado
            else:
                terreno_txt += '.'
            terreno_txt += '</td>'
        terreno_txt += '</tr>'
    terreno_txt += '</table>'
    return terreno_txt

def mover_jugador(direccion):
    global jugador_x, jugador_y, camuflado, imagen_jugador, imagen_bonshot_besado
    mensaje = ""
    ganaste = False  # 🔥 nuevo flag

    if imagen_bonshot_besado:
        imagen_jugador = "img/woofzn.png" if not camuflado else "img/camouflage.png"
        imagen_bonshot_besado = False

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
        imagen_jugador = "img/camouflage.png" if camuflado else "img/woofzn.png"
        mensaje = "Youre camouflaged!" if camuflado else "You stopped camouflaging!"


    # Revisar si beso bonshot
    for bonshot in bonshots:
        bx, by, besado = bonshot
        if bx == jugador_x and by == jugador_y and not besado:
            if not camuflado:
                bonshot[2] = True
                mensaje = "You kissed a bonshot!"
                imagen_jugador = "img/kissy.png"
                imagen_bonshot_besado = True
            else:
                mensaje = "You cant kiss bonshot while being camouflaged!!"

    # Ganar si todos besados
    if all(besado for _, _, besado in bonshots):
        mensaje = "All bonshots have been kissed! You win!"
        ganaste = True  # 🔥 ahora sí marcamos como ganado

    return mensaje, ganaste

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mover', methods=['POST'])
def mover():
    global jugador_x, jugador_y, camuflado
    data = request.json
    direccion = data.get('direccion', '')

    if direccion == '':
        jugador_x = ANCHO // 2
        jugador_y = ALTO // 2
        camuflado = False
        inicializar_bonshots()

    mensaje, ganaste = mover_jugador(direccion.upper())
    return jsonify({
        'terreno': render_terreno(),
        'mensaje': mensaje,
        'ganaste': ganaste  # 🔥 enviamos flag al JS
    })

if __name__ == '__main__':
    app.run(debug=True)
