const terrenoDiv = document.getElementById('terreno');
const mensajeDiv = document.getElementById('mensaje');
const reglasDiv = document.getElementById('reglas');
const jugarBtn = document.getElementById('jugarBtn');
const volverBtn = document.getElementById('volverBtn');

let jugando = false;

// Función para iniciar el juego
function iniciarJuego() {
    jugando = true;
    reglasDiv.style.display = 'none';
    jugarBtn.style.display = 'none';
    terrenoDiv.style.display = 'block';
    mensajeDiv.style.display = 'block';
    volverBtn.style.display = 'none';
    
    mover('');  // Renderiza el terreno sin mover al principio
}

// Función para mostrar el botón de "volver a jugar" al perder
function terminarJuego() {
    jugando = false;
    volverBtn.style.display = 'block';
    mensajeDiv.innerText = "¡Perdiste! Haz clic en 'Volver a jugar' para intentar de nuevo.";
}

async function mover(direccion) {
    if (!jugando) return;

    const response = await fetch('/mover', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ direccion })
    });

    const data = await response.json();
    terrenoDiv.innerHTML = data.terreno;  // Usamos innerHTML para manejar las imágenes del jugador
    mensajeDiv.innerText = data.mensaje;

    // Si se pierde, mostrar el mensaje de "perdiste"
    if (data.mensaje.includes("perdiste")) {
        terminarJuego();
    }
}

// Detectar las teclas
document.addEventListener('keydown', (e) => {
    const tecla = e.key.toUpperCase();
    if (['W', 'A', 'S', 'D', 'Q'].includes(tecla)) {
        mover(tecla);
    }
});
