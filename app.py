from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- Juego: Estado global ---
ANCHO = 20
ALTO = 10
terreno = [['.' for _ in range(ANCHO)] for _ in range(ALTO)]
jugador_x = ANCHO // 2
jugador_y = ALTO // 2
camuflado = False

def render_terreno():
    terreno_html = ''
    for y in range(ALTO):
        for x in range(ANCHO):
            if x == jugador_x and y == jugador_y:
                if camuflado:
                    terreno_html += '<img src="/static/camuflado.png" class="jugador"/>'
                else:
                    terreno_html += '<img src="/static/personaje.png" class="jugador"/>'
            else:
                terreno_html += '.'
        terreno_html += '<br>'
    return terreno_html

def mover_jugador(direccion):
    global jugador_x, jugador_y, camuflado
    mensaje = ""

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
    else:
        mensaje = "Movimiento no válido"
    
    # Condición de pérdida (si el jugador sale del terreno)
    if jugador_x < 0 or jugador_x >= ANCHO or jugador_y < 0 or jugador_y >= ALTO:
        mensaje = "¡Perdiste! Saliste del terreno."

    return mensaje

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/mover', methods=['POST'])
def mover():
    data = request.json
    direccion = data.get('direccion', '')
    mensaje = mover_jugador(direccion.upper())
    return jsonify({
        'terreno': render_terreno(),
        'mensaje': mensaje
    })

if __name__ == '__main__':
    app.run(debug=True)
