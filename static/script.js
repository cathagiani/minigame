const vidasDiv = document.getElementById('vidas');
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
    vidasDiv.innerText = "Vidas restantes: 3";
    
    mover('');  // Renderiza el terreno sin mover al principio
}

// Función para mostrar el botón de "volver a jugar"
function terminarJuego() {
    jugando = false;
    volverBtn.style.display = 'block';
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
    terrenoDiv.innerHTML = data.terreno;  
    mensajeDiv.innerText = data.mensaje;
    vidasDiv.innerText = `Vidas restantes: ${data.vidas}`;

    if (data.ganaste) {  // 🔥 ahora sí sabremos si se ganó
        terminarJuego();
    }
}

document.addEventListener('keydown', (e) => {
    const tecla = e.key.toUpperCase();
    if (['W', 'A', 'S', 'D', 'Q'].includes(tecla)) {
        e.preventDefault();  // ⬅️ evita el scroll o acción por defecto del navegador
        mover(tecla);
    }
});

volverBtn.addEventListener('click', () => {
    iniciarJuego();
});