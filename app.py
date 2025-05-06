from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

# --- Juego: Estado global ---
ANCHO = 6
ALTO = 6
terreno = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
jugador_x = ANCHO // 2
jugador_y = ALTO // 2
camuflado = False
imagen_jugador = "img/woofzn.png"
imagen_bonshot_besado = False
vidas = 3
imagen_loveletter = False

# Lista de bonshots
bonshots = []
cartas_amor = []
spiders = []

def inicializar_bonshots():
    global bonshots, cartas_amor
    bonshots = []
    cantidad = random.randint(5, 10)
    while len(bonshots) < cantidad:
        x = random.randint(0, ANCHO - 1)
        y = random.randint(0, ALTO - 1)
        if (x, y) != (jugador_x, jugador_y) and (x, y) not in [b[:2] for b in bonshots]:
            bonshots.append([x, y, False])  # [x, y, besado=False]
    
    # Inicializar 4 cartas de amor (love letters)
    cartas_amor = []
    while len(cartas_amor) < 4:
        x = random.randint(0, ANCHO - 1)
        y = random.randint(0, ALTO - 1)
        if (x, y) != (jugador_x, jugador_y) \
           and (x, y) not in [b[:2] for b in bonshots] \
           and (x, y) not in cartas_amor:
            cartas_amor.append((x, y))

def inicializar_spiders():
    global spiders
    spiders = []
    while len(spiders) < 2:
        x = random.randint(0, ANCHO - 1)
        y = random.randint(0, ALTO - 1)
        if (x, y) != (jugador_x, jugador_y) and (x, y) not in [b[:2] for b in bonshots] and (x, y) not in cartas_amor:
            direccion = random.choice([0, 1])  # 0 = horizontal, 1 = vertical
            spiders.append([x, y, direccion])

def render_terreno():
    terreno_txt = '<table class="matriz">'
    for y in range(ALTO):
        terreno_txt += '<tr>'
        for x in range(ANCHO):
            terreno_txt += '<td>'
            if x == jugador_x and y == jugador_y:
                # Mostrar imagen según los flags
                if imagen_loveletter:
                    src = "img/woofzn-luvletter.png"
                elif imagen_bonshot_besado:
                    src = "img/kissy.png"
                else:
                    src = imagen_jugador
                terreno_txt += f'<img src="/static/{src}" class="jugador">'
            elif any(bx == x and by == y and not besado for bx, by, besado in bonshots):
                terreno_txt += '<img src="/static/img/bonshot.png" class="bonshot">'
            elif any(bx == x and by == y and besado for bx, by, besado in bonshots):
                terreno_txt += '<img src="/static/img/kissedbonshot.png" class="bonshot">'
            elif (x, y) in cartas_amor:
                terreno_txt += '<img src="/static/img/luvletter.png" class="loveletter">'
            elif any(sx == x and sy == y for sx, sy, _ in spiders):
                terreno_txt += '<img src="/static/img/spider.png" class="spider">'  # Imagen que agregarás
            else:
                terreno_txt += '.'
            terreno_txt += '</td>'
        terreno_txt += '</tr>'
    terreno_txt += '</table>'
    return terreno_txt

def mover_spiders():
    global spiders
    for spider in spiders:
        x, y, direccion = spider
        if direccion == 0:  # horizontal
            x += 1
            if x >= ANCHO:
                x = 0  # vuelve al inicio
        else:  # vertical
            y += 1
            if y >= ALTO:
                y = 0  # vuelve al inicio
        spider[0] = x
        spider[1] = y

def mover_jugador(direccion):
    global jugador_x, jugador_y, camuflado, imagen_jugador, imagen_bonshot_besado, vidas, cartas_amor, imagen_loveletter
    mensaje = ""
    ganaste = False
    imagen_jugador_original = "img/woofzn.png"  # Imagen original de Woofzn (normal)

    if vidas <= 0:
        mensaje = "Game Over! You lost all your lives!"
        ganaste = False
        return mensaje, ganaste

    imagen_loveletter = False
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
        mensaje = "You're camouflaged!" if camuflado else "You stopped camouflaging!"

    # Revisar si beso bonshot
    for bonshot in bonshots:
        bx, by, besado = bonshot
        if bx == jugador_x and by == jugador_y and not besado:
            if not camuflado:
                bonshot[2] = True
                mensaje = "You kissed a bonshot!"
                imagen_bonshot_besado = True  # 🔥 activamos flag por 1 turno
            else:
                mensaje = "You can't kiss bonshot while being camouflaged!!"
    
    # Capturar la love letter
    if (jugador_x, jugador_y) in cartas_amor and not camuflado:
        vidas += 1
        cartas_amor.remove((jugador_x, jugador_y))
        mensaje = "You found a love letter! +1 life"
        imagen_loveletter = True  # 🔥 activamos flag por 1 turno

    # Ganar si todos besados
    if all(besado for _, _, besado in bonshots):
        mensaje = "All bonshots have been kissed! You win!"
        ganaste = True

    mover_spiders()
    for sx, sy, _ in spiders:
        if not camuflado and (
            (sx == jugador_x and sy == jugador_y) or  # 🔥 encima de la spider
            (abs(sx - jugador_x) == 1 and sy == jugador_y) or  # izquierda o derecha
            (abs(sy - jugador_y) == 1 and sx == jugador_x)     # arriba o abajo
        ):
            vidas -= 1
            mensaje = "A spider hurt you! -1 life"
            break  # solo perder una vida por turno
            
    return mensaje, ganaste

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mover', methods=['POST'])
def mover():
    global jugador_x, jugador_y, camuflado, vidas
    data = request.json
    direccion = data.get('direccion', '')

    if direccion == '':
        jugador_x = ANCHO // 2
        jugador_y = ALTO // 2
        camuflado = False
        inicializar_bonshots()
        inicializar_spiders()
        vidas = 3

    mensaje, ganaste = mover_jugador(direccion.upper())

    perdiste = vidas <= 0

    return jsonify({
        'terreno': render_terreno(),
        'mensaje': mensaje,
        'ganaste': ganaste,
        'perdiste': perdiste,
        'vidas': vidas,
    })


if __name__ == '__main__':
    app.run(debug=True)