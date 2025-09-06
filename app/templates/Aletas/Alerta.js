// Coloca este código en un archivo llamado alerta.js
function validarFormulario(formularioId) {
    const formulario = document.getElementById(formularioId);
    if (!formulario) {
        console.error(`Error: No se encontró el formulario con el ID "${formularioId}".`);
        return [];
    }

    const camposFaltantes = [];
    const campos = formulario.querySelectorAll('[required]');

    campos.forEach(campo => {
        if (campo.type === 'file' && campo.files.length === 0) {
            const etiqueta = campo.previousElementSibling.innerText || campo.id;
            camposFaltantes.push(etiqueta);
        } else if (campo.value.trim() === '') {
            const etiqueta = campo.previousElementSibling.innerText || campo.id;
            camposFaltantes.push(etiqueta);
        }
    });

    return camposFaltantes;
}

function mostrarAlerta(errores) {
    const alerta = document.getElementById('alertPlaceholder');
    const lista = document.getElementById('listaErrores');
    const fondo = document.getElementById('fondoModal');

    if (errores.length > 0) {
        lista.innerHTML = ''; 

        errores.forEach(error => {
            const li = document.createElement('li');
            li.textContent = error;
            lista.appendChild(li);
        });

        alerta.classList.remove('d-none');
        fondo.classList.remove('d-none');
        setTimeout(() => {
            alerta.classList.add('show');
        }, 10);
    } else {
        alerta.classList.remove('show');
        setTimeout(() => {
            alerta.classList.add('d-none');
            fondo.classList.add('d-none');
        }, 150);
    }
}

// Ejemplo de uso
const form = document.getElementById('tuFormularioId'); // Reemplaza 'tuFormularioId' por el ID de tu formulario

form.addEventListener('submit', function(event) {
    event.preventDefault(); // Evita el envío del formulario por defecto

    const camposIncompletos = validarFormulario(this.id); // 'this.id' para obtener el ID del formulario actual

    if (camposIncompletos.length > 0) {
        mostrarAlerta(camposIncompletos);
    } else {
        // Si no hay campos incompletos, puedes continuar con el envío del formulario o la lógica de tu aplicación
        mostrarAlerta([]); // Oculta la alerta si ya estaba visible
        console.log('Formulario completado correctamente. Listo para enviar.');
        // Aquí iría tu lógica para enviar los datos, por ejemplo:
        // form.submit();
    }
});
