/* PLANTILLA HEADER - SIDE BAR */

// ACÁ: Manejo de la apertura/cierre del sidebar y menú de usuario
const toggleBtn = document.getElementById("toggleSidebar");
const closeBtn = document.getElementById("closeSidebar");
const sidebar = document.getElementById("sidebar");
const body = document.body;

const profileIcon = document.getElementById('profileIcon');
const dropdownMenu = document.getElementById('dropdownMenu');
const userNameDisplay = document.getElementById('userName');
const logoutBtn = document.getElementById('logoutBtn');

/**
 * ACÁ: Muestra la inicial y el nombre del usuario en el header.
 * @param {string} name - Nombre del usuario.
 */
function setUserInitial(name) {
    const initial = name.trim().charAt(0).toUpperCase();
    profileIcon.textContent = initial;
    userNameDisplay.textContent = name;
}

// ACÁ: Inicializa el nombre del usuario (debe ser reemplazado por el real)
setUserInitial("Nombre de Prueba");

// ACÁ: Abre/cierra el menú de usuario al hacer click en el icono de perfil
profileIcon.addEventListener('click', () => {
    dropdownMenu.classList.toggle('show');
});

// ACÁ: Oculta el menú de usuario si se hace clic fuera de él
document.addEventListener('click', (event) => {
    if (
        !profileIcon.contains(event.target) &&
        !dropdownMenu.contains(event.target)
    ) {
        dropdownMenu.classList.remove('show');
    }
});

// ACÁ: Acción de cerrar sesión (debe ser reemplazada por la lógica real)
logoutBtn.addEventListener('click', () => {
    alert("Sesión cerrada");
});

// ACÁ: Abre el sidebar al hacer click en el botón hamburguesa
toggleBtn.addEventListener("click", () => {
    sidebar.classList.add("show");
    toggleBtn.classList.add("hide");
});

// ACÁ: Cierra el sidebar al hacer click en el botón de cerrar
closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("show");
    toggleBtn.classList.remove("hide"); 
});

// ACÁ: Cierra el sidebar si se hace click fuera de él
document.addEventListener('click', function (event) {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');

  if (
    sidebar.classList.contains('show') &&
    !sidebar.contains(event.target) &&
    !toggleBtn.contains(event.target)
  ) {
    sidebar.classList.remove('show');
    toggleBtn.classList.remove('hide');
  }
});

/***************** FUNCIONES VIEW *********************************/

/**
 * ACÁ: Valida si un RUT chileno es válido.
 * @param {string} rut - RUT a validar.
 * @returns {boolean} true si es válido, false si no.
 */
function validarRut(rut) {
  rut = rut.replace(/^0+|[^0-9kK]+/g, '').toUpperCase();
  if (rut.length < 2) return false;
  let cuerpo = rut.slice(0, -1);
  let dv = rut.slice(-1);
  let suma = 0, multiplo = 2;
  for (let i = cuerpo.length - 1; i >= 0; i--) {
    suma += parseInt(cuerpo[i]) * multiplo;
    multiplo = multiplo < 7 ? multiplo + 1 : 2;
  }
  let dvEsperado = 11 - (suma % 11);
  dvEsperado = dvEsperado === 11 ? '0' : dvEsperado === 10 ? 'K' : dvEsperado.toString();
  return dv === dvEsperado;
}

/**********************************************
 ************** DOMContentLoaded **************
 **********************************************/

// ACÁ: Valida el RUT cuando el usuario termina de escribirlo
const rutInput = document.getElementById('rutTrabajador');
if (rutInput) {
  rutInput.addEventListener('blur', function () {
    if (!validarRut(rutInput.value)) {
      rutInput.classList.add('is-invalid');
      rutInput.setCustomValidity('RUT inválido');
    } else {
      rutInput.classList.remove('is-invalid');
      rutInput.setCustomValidity('');
    }
  });
}

// ACÁ: Valida que el teléfono personal tenga al menos 8 dígitos
const telefonoPersonalInput = document.getElementById('telefonoPersonal');
if (telefonoPersonalInput) {
  telefonoPersonalInput.addEventListener('input', function () {
    if (telefonoPersonalInput.value.length < 8) {
      telefonoPersonalInput.classList.add('is-invalid');
      telefonoPersonalInput.setCustomValidity('Debe tener al menos 8 dígitos');
    } else {
      telefonoPersonalInput.classList.remove('is-invalid');
      telefonoPersonalInput.setCustomValidity('');
    }
  });
}

// ACÁ: Muestra el campo "Plan en UF" solo si la institución de salud no es FONASA
const planUfContainer = document.getElementById('planUfContainer');
const selectSalud = document.getElementById('salud');
if (selectSalud && planUfContainer) {
  selectSalud.addEventListener('change', function () {
    if (selectSalud.value.trim().toLowerCase() !== 'fonasa') {
      planUfContainer.style.display = 'block';
    } else {
      planUfContainer.style.display = 'none';
    }
  });
}

// ACÁ: Muestra la vista previa de la foto del trabajador cuando se selecciona un archivo
    document.getElementById('fotoTrabajador').addEventListener('change', function(event) {
      const [file] = event.target.files;
      if (file) {
        const preview = document.getElementById('previewFoto');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
        const fotoArribaDerecha = document.getElementById('fotoArribaDerecha');
        fotoArribaDerecha.src = URL.createObjectURL(file);
        fotoArribaDerecha.style.display = 'block';
      }
    });
    // ACÁ: Muestra la vista previa de la foto carnet frontal cuando se selecciona un archivo
    document.getElementById('fotoCarnetFrontal').addEventListener('change', function(event) {
      const [file] = event.target.files;
      if (file) {
        const preview = document.getElementById('previewCarnetFrontal');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
      }
    });
    // ACÁ: Muestra la vista previa de la foto carnet reverso cuando se selecciona un archivo
    document.getElementById('fotoCarnetReverso').addEventListener('change', function(event) {
      const [file] = event.target.files;
      if (file) {
        const preview = document.getElementById('previewCarnetReverso');
        preview.src = URL.createObjectURL(file);
        preview.style.display = 'block';
      }
    }); 
    // ACÁ: Inicializa Choices.js en los selects indicados y flatpickr en los campos de fecha
    document.addEventListener('DOMContentLoaded', async function() {
      // Mapeo de select id a endpoint
      const selectEndpoints = {
        nacionalidadTrabajador: 'paises',
        region: 'regiones',
        comuna: 'comunas',
        afp: 'afps',
        salud: 'instituciones-salud',
        jefe: 'jefes'
        // Puedes agregar más si tu backend los soporta
      };

      // Carga dinámica de opciones para cada select
      for (const [selectId, endpoint] of Object.entries(selectEndpoints)) {
        const select = document.getElementById(selectId);
        if (select) {
          try {
            const res = await fetch(`http://localhost:3000/${endpoint}`);
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            select.innerHTML = '<option value="">Seleccione...</option>' +
              data.map(opt => `<option value="${opt}">${opt}</option>`).join('');
          } catch (e) {
            console.error(`Error cargando ${endpoint}:`, e); // <-- Agregado para depuración
            select.innerHTML = `<option value="">Error al cargar opciones (${e.message})</option>`;
          }
        }
      }

      // Inicializa Choices.js después de llenar los selects
      const selects = [
        'nacionalidadTrabajador',
        'estadoCivil',
        'region',
        'comuna',
        'afp',
        'salud',
        'cargo',
        'formaPago',
        'sexo',
        'jefe'
      ];
      selects.forEach(function(id) {
        const el = document.getElementById(id);
        if (el) {
          new Choices(el, {
            searchEnabled: true,
            itemSelectText: '',
            shouldSort: false
          });
        }
      });
      
      // ACÁ: Inicializa flatpickr en los campos de fecha
      const fechaNacimiento = document.getElementById('fechaNacimientoTrabajador');
      if (fechaNacimiento) {
        flatpickr(fechaNacimiento, {
          dateFormat: "Y-m-d",
          minDate: new Date().getFullYear() - 100 + "-01-01",
          maxDate: new Date().getFullYear() - 15 + "-12-31"
        });
      }
      const fechaIngreso = document.getElementById('fechaIngreso');
      if (fechaIngreso) {
        flatpickr(fechaIngreso, {
          dateFormat: "Y-m-d",
          maxDate: "today"
        });
      }
      const fechaContrato = document.getElementById('fechaContrato');
      if (fechaContrato) {
        flatpickr(fechaContrato, {
          dateFormat: "Y-m-d",
          maxDate: "today"
        });
      }
    });

  // ACÁ: Envía el formulario de datos del trabajador al backend usando fetch
  document.getElementById('form-datos-empresa').addEventListener('submit', function(e) {
    e.preventDefault(); // Evita el envío tradicional
    const formData = new FormData(this);

    fetch('http://localhost:3000/trabajadores', { // URL de tu backend
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      // Mostrar los datos recibidos del backend en un alert o en consola
      alert('Datos enviados correctamente:\n' + JSON.stringify(data, null, 2));
      // También puedes mostrar los datos en el DOM si prefieres
      // document.getElementById('resultadosEnvio').textContent = JSON.stringify(data, null, 2);
    })
    .catch(err => {
      alert('Error al enviar los datos');
    });
  });

    // ACÁ: (Ejemplo comentado) Mostrar contratos del trabajador obtenidos desde el backend
    document.addEventListener('DOMContentLoaded', function() {
      const listaContratos = document.getElementById('listaContratos');
      // Cambiado a la URL real del backend
      fetch('http://localhost:3000/contratos')
        .then(res => res.json())
        .then(data => {
          if (Array.isArray(data)) {
            listaContratos.innerHTML = '';
            data.forEach(function(contrato, idx) {
              const li = document.createElement('li');
              li.className = 'list-group-item d-flex align-items-center justify-content-between';
              li.innerHTML = `
                <span>${contrato.nombre}</span>
                <div class="btn-group btn-group-sm" role="group">
                  <a href="${contrato.url}" target="_blank" class="btn btn-outline-primary" title="Ver">
                    <i class="bi bi-eye"></i>
                  </a>
                  <a href="${contrato.url}" download class="btn btn-outline-success" title="Descargar">
                    <i class="bi bi-download"></i>
                  </a>
                  <button type="button" class="btn btn-outline-danger" title="Eliminar" data-idx="${idx}">
                    <i class="bi bi-trash"></i>
                  </button>
                </div>
              `;
              listaContratos.appendChild(li);
            });
          }
        });
    });

  // ACÁ: Agrega un listener para manejar la eliminación de contratos en el frontend
  document.addEventListener('DOMContentLoaded', function() {
    const listaContratos = document.getElementById('listaContratos');
    listaContratos.addEventListener('click', function(e) {
      const btn = e.target.closest('button[data-idx]');
      if (btn) {
        // Elimina el contrato del DOM
        btn.closest('li').remove();
        // Si quieres eliminar en el backend, aquí puedes hacer un fetch al backend
        // Ejemplo:
        // const contratoNombre = btn.closest('li').querySelector('span').textContent;
        // fetch('http://localhost:3000/contratos/eliminar', {
        //   method: 'POST',
        //   headers: { 'Content-Type': 'application/json' },
        //   body: JSON.stringify({ nombre: contratoNombre })
        // });
      }
    });
  });

  // ACÁ: Muestra u oculta los formularios según la acción seleccionada (nuevo/buscar trabajador)
  document.addEventListener('DOMContentLoaded', function() {
    const btnNuevo = document.getElementById('btnNuevoTrabajador');
    const btnBuscar = document.getElementById('btnBuscarTrabajador');
    const busquedaDiv = document.getElementById('busquedaTrabajador');
    const formDatos = document.getElementById('form-datos-empresa');
    btnNuevo.addEventListener('click', function() {
      busquedaDiv.style.display = 'none';
      formDatos.style.display = '';
    });
    btnBuscar.addEventListener('click', function() {
      busquedaDiv.style.display = '';
      formDatos.style.display = 'none';
    });
  
    // ACÁ: Realiza la búsqueda de trabajadores en el backend y muestra los resultados
    document.getElementById('formBusquedaTrabajador').addEventListener('submit', function(e) {
      e.preventDefault();
      const nombre = document.getElementById('busquedaNombre').value;
      const rut = document.getElementById('busquedaRut').value;
      const cargo = document.getElementById('busquedaCargo').value;
      const resultadosDiv = document.getElementById('resultadosBusqueda');

      // Cambiado a la URL real del backend
      fetch('http://localhost:3000/buscar-trabajadores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          nombre: nombre,
          rut: rut,
          cargo: cargo
        })
      })
      .then(res => res.json())
      .then(resultados => {
        if (!Array.isArray(resultados) || resultados.length === 0) {
          resultadosDiv.innerHTML = '<div class="alert alert-warning">No se encontraron trabajadores.</div>';
        } else {
          resultadosDiv.innerHTML = '<ul class="list-group">' +
            resultados.map(t =>
              `<li class="list-group-item d-flex justify-content-between align-items-center">
                <span>
                  <strong>${t.nombre}</strong> - ${t.rut} - ${t.cargo}
                </span>
                <button class="btn btn-sm btn-outline-success" onclick="verTrabajador('${t.rut}')">
                  <i class="bi bi-pencil"></i> Ver/Editar
                </button>
              </li>`
            ).join('') +
            '</ul>';
        }
      })
      .catch(() => {
        resultadosDiv.innerHTML = '<div class="alert alert-danger">Error al buscar trabajadores.</div>';
      });
    });
  });
  
  // ACÁ: Función para ver/editar trabajador (debes cargar los datos reales del backend)
  function verTrabajador(rut) {
    //? Debes pedir al backend: datos completos del trabajador con el rut dado
    //? Ejemplo de datos esperados: { nombre, rut, fechaNacimiento, sexo, nacionalidad, ... }
    alert('Cargar datos del trabajador con RUT: ' + rut);
    document.getElementById('busquedaTrabajador').style.display = 'none';
    document.getElementById('form-datos-empresa').style.display = '';
  }

  // ACÁ: Manejo de subida y listado de documentos personales/laborales
  document.addEventListener('DOMContentLoaded', function() {
    const inputDocumentos = document.getElementById('inputDocumentos');
    const listaDocumentos = document.getElementById('listaDocumentos');
    let documentosSubidos = []; // [{nombre, url}]

    // ACÁ: Renderiza la lista de documentos subidos
    function renderListaDocumentos() {
      listaDocumentos.innerHTML = '';
      documentosSubidos.forEach((doc, idx) => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `
          <span>${doc.nombre}</span>
          <div class="btn-group btn-group-sm" role="group">
            <a href="${doc.url}" target="_blank" class="btn btn-outline-primary" title="Ver">
              <i class="bi bi-eye"></i>
            </a>
            <a href="${doc.url}" download class="btn btn-outline-success" title="Descargar">
              <i class="bi bi-download"></i>
            </a>
            <button type="button" class="btn btn-outline-danger" title="Eliminar" data-idx="${idx}">
              <i class="bi bi-trash"></i>
            </button>
          </div>
        `;
        listaDocumentos.appendChild(li);
      });
    }

    // ACÁ: Elimina un documento de la lista y del backend
    listaDocumentos.addEventListener('click', function(e) {
      if (e.target.closest('button[data-idx]')) {
        const idx = e.target.closest('button[data-idx]').getAttribute('data-idx');
        const doc = documentosSubidos[idx];
        // Cambiado a la URL real del backend
        fetch('http://localhost:3000/documentos/eliminar', {
          method: 'POST',
          body: JSON.stringify({ nombre: doc.nombre }),
          headers: { 'Content-Type': 'application/json' }
        }).then(() => {
          documentosSubidos.splice(idx, 1);
          renderListaDocumentos();
        }).catch(() => {
          alert('Error al eliminar el documento');
        });
      }
    });

    // ACÁ: Sube documentos al backend y actualiza la lista
    inputDocumentos.addEventListener('change', function(e) {
      const files = Array.from(e.target.files);
      if (files.length === 0) return;
      const formData = new FormData();
      files.forEach(f => formData.append('documentos', f));
      // Cambiado a la URL real del backend
      fetch('http://localhost:3000/documentos/subir', {
        method: 'POST',
        body: formData
      })
      .then(res => res.json())
      .then(data => {
        // data: [{nombre, url}, ...]
        if (Array.isArray(data)) {
          documentosSubidos = documentosSubidos.concat(data);
          renderListaDocumentos();
        }
        inputDocumentos.value = ''; // Limpiar input
      })
      .catch(() => {
        alert('Error al subir documentos');
      });
    });

    // ACÁ: (Ejemplo comentado) Carga documentos existentes al cargar la página
    // Cambiado a la URL real del backend
    fetch('http://localhost:3000/documentos/listar')
        .then(res => res.json())
        .then(data => {
          documentosSubidos = data;
          renderListaDocumentos();
        });

  });
document.addEventListener('DOMContentLoaded', function () {
  const foto = document.getElementById('fotoArribaDerecha');
  const modalDescarga = document.getElementById('modalDescargaImagen');
  const modalEliminar = document.getElementById('modalEliminarFoto');
  const fondo = document.getElementById('fondoModalDescarga');

  const btnDescargar = document.getElementById('btnDescargarFoto');
  const btnEliminar = document.getElementById('btnEliminarFoto');
  const btnConfirmarDescarga = document.getElementById('confirmarDescargaBtn');
  const btnCancelarDescarga = document.getElementById('cancelarDescargaBtn');
  const btnConfirmarEliminar = document.getElementById('confirmarEliminarBtn');
  const btnCancelarEliminar = document.getElementById('cancelarEliminarBtn');
  const btnAgregarFoto = document.getElementById('btnAgregarFoto');
  const inputAgregarFoto = document.getElementById('inputAgregarFoto');
  const fotoArribaDerecha = document.getElementById('fotoArribaDerecha');

  const inputFoto = document.getElementById('fotoTrabajador');
  const previewFoto = document.getElementById('previewFoto');

  // ----- Modal de DESCARGA -----
  if (btnDescargar) {
    btnDescargar.addEventListener('click', () => {
      modalDescarga.style.display = 'block';
      fondo.style.display = 'block';
    });

    btnCancelarDescarga.addEventListener('click', () => {
      modalDescarga.style.display = 'none';
      fondo.style.display = 'none';
    });

    btnConfirmarDescarga.addEventListener('click', () => {
      const link = document.createElement('a');
      link.href = foto.src;
      link.download = 'foto_trabajador.jpg';
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      modalDescarga.style.display = 'none';
      fondo.style.display = 'none';
    });
  }

  // ----- Modal de ELIMINACIÓN -----
  if (btnEliminar) {
    btnEliminar.addEventListener('click', () => {
      modalEliminar.style.display = 'block';
      fondo.style.display = 'block';
    });

    btnCancelarEliminar.addEventListener('click', () => {
      modalEliminar.style.display = 'none';
      fondo.style.display = 'none';
    });

    btnConfirmarEliminar.addEventListener('click', () => {
      foto.src = 'img/inicio.png'; // Imagen por defecto nueva
      if (inputFoto) inputFoto.value = '';
      if (previewFoto) previewFoto.style.display = 'none';

      modalEliminar.style.display = 'none';
      fondo.style.display = 'none';
    });
  }

  // ----- AGREGAR FOTO -----
  if (btnAgregarFoto && inputAgregarFoto && fotoArribaDerecha) {
    btnAgregarFoto.addEventListener('click', () => {
      inputAgregarFoto.click();
    });

    inputAgregarFoto.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        const nuevaSrc = URL.createObjectURL(file);
        fotoArribaDerecha.src = nuevaSrc;
      }
    });
  }

});



