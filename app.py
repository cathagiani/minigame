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
vidas = 3
imagen_loveletter = False

# Lista de bonshots
bonshots = []
cartas_amor = []

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
                terreno_txt += '<img src="/static/img/bonshot.png" class="bonshot">'  # Bonshot activo
            elif any(bx == x and by == y and besado for bx, by, besado in bonshots):
                terreno_txt += '<img src="/static/img/kissedbonshot.png" class="bonshot">'  # Bonshot besado
            elif (x, y) in cartas_amor:
                terreno_txt += '<img src="/static/img/luvletter.png" class="loveletter">'
            else:
                terreno_txt += '.'
            terreno_txt += '</td>'
        terreno_txt += '</tr>'
    terreno_txt += '</table>'
    return terreno_txt

def mover_jugador(direccion):
    global jugador_x, jugador_y, camuflado, imagen_jugador, imagen_bonshot_besado, vidas, cartas_amor, imagen_loveletter
    mensaje = ""
    ganaste = False

    if vidas <= 0:
        mensaje = "¡Game Over! You lost all your lives!"
        ganaste = False
        vidas = 3  # Reiniciar las vidas cuando se pierden todas

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

    mensaje, ganaste = mover_jugador(direccion.upper())
    return jsonify({
        'terreno': render_terreno(),
        'mensaje': mensaje,
        'ganaste': ganaste, # 🔥 enviamos flag al JS
        'vidas': vidas,  # Enviamos el número de vidas restantes
    })

if __name__ == '__main__':
    app.run(debug=True)
