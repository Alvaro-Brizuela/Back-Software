
/* HEADER - SIDEBAR */
const toggleBtn = document.getElementById("toggleSidebar");
const closeBtn = document.getElementById("closeSidebar");
const sidebar = document.getElementById("sidebar");
const body = document.body;

const profileIcon = document.getElementById('profileIcon');
const dropdownMenu = document.getElementById('dropdownMenu');
const userNameDisplay = document.getElementById('userName');
const logoutBtn = document.getElementById('logoutBtn');

function setUserInitial(name) {
  const initial = name.trim().charAt(0).toUpperCase();
  profileIcon.textContent = initial;
  userNameDisplay.textContent = name;
}
setUserInitial("Felipe Moscoso");

profileIcon.addEventListener('click', () => {
  dropdownMenu.classList.toggle('show');
});

document.addEventListener('click', (event) => {
  if (!profileIcon.contains(event.target) && !dropdownMenu.contains(event.target)) {
    dropdownMenu.classList.remove('show');
  }
});

logoutBtn.addEventListener('click', () => {
  alert("Sesión cerrada");
});

toggleBtn.addEventListener("click", () => {
  sidebar.classList.add("show");
  toggleBtn.classList.add("hide");
});

closeBtn.addEventListener("click", () => {
  sidebar.classList.remove("show");
  toggleBtn.classList.remove("hide");
});

document.addEventListener('click', function (event) {
  if (
    sidebar.classList.contains('show') &&
    !sidebar.contains(event.target) &&
    !toggleBtn.contains(event.target)
  ) {
    sidebar.classList.remove('show');
    toggleBtn.classList.remove('hide');
  }
});

/* FUNCIONES VIEW */

const formCargo = document.getElementById("formCargo");
const listaCargos = document.getElementById("listaCargos");
const nombreInput = document.getElementById("nombreCargo");
const descripcionInput = document.getElementById("descripcionCargo");
const buscadorInput = document.getElementById("buscadorCargo");

let cargos = [];

// Validar si el nombre ya existe
function validarNombreExistente(nombre) {
  return cargos.some(c => c.nombre.toLowerCase() === nombre.toLowerCase());
}

// Evento guardar cargo
formCargo.addEventListener("submit", async (e) => {
  e.preventDefault();

  const nombre = nombreInput.value.trim();
  const descripcion = descripcionInput.value.trim();

  if (!nombre) return;
  if (validarNombreExistente(nombre)) {
    nombreInput.classList.add("is-invalid");
    return;
  }

  nombreInput.classList.remove("is-invalid");

  const nuevoCargo = await guardarCargoEnBackend(nombre, descripcion);

  if (nuevoCargo) {
    alert("Cargo guardado correctamente.");
    formCargo.reset();
    await recargarCargos();
  } else {
    alert("Hubo un error al guardar el cargo.");
  }
});

// Renderizar lista de cargos
function actualizarListaCargos(filtro = "") {
  listaCargos.innerHTML = "";

  const cargosFiltrados = cargos.filter(c =>
    c.nombre.toLowerCase().includes(filtro.toLowerCase())
  );

  if (cargosFiltrados.length === 0) {
    const li = document.createElement("li");
    li.className = "list-group-item text-center text-muted";
    li.textContent = "No hay cargos registrados.";
    listaCargos.appendChild(li);
    return;
  }

  cargosFiltrados.forEach((cargo, indexOriginal) => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex justify-content-between align-items-center fade-in";

    const span = document.createElement("span");
    span.innerHTML = `<strong>${cargo.nombre}</strong><br><small>${cargo.descripcion}</small>`;

    const btnEditar = document.createElement("button");
    btnEditar.className = "btn btn-sm btn-outline-primary me-2";
    btnEditar.innerHTML = '<i class="bi bi-pencil"></i>';
    btnEditar.onclick = () => {
      nombreInput.value = cargo.nombre;
      descripcionInput.value = cargo.descripcion;
      cargos.splice(indexOriginal, 1);
      actualizarListaCargos(buscadorInput.value);
    };

    const btnEliminar = document.createElement("button");
    btnEliminar.className = "btn btn-sm btn-outline-danger";
    btnEliminar.innerHTML = '<i class="bi bi-trash"></i>';
    btnEliminar.onclick = () => {
      if (confirm(`¿Eliminar el cargo "${cargo.nombre}"?`)) {
        li.classList.add("fade-out");
        setTimeout(() => {
          cargos.splice(indexOriginal, 1);
          actualizarListaCargos(buscadorInput.value);
        }, 300);
      }
    };

    const acciones = document.createElement("div");
    acciones.className = "d-flex";
    acciones.appendChild(btnEditar);
    acciones.appendChild(btnEliminar);

    li.appendChild(span);
    li.appendChild(acciones);
    listaCargos.appendChild(li);
  });
}

// Filtro en tiempo real
if (buscadorInput) {
  buscadorInput.addEventListener("input", () => {
    actualizarListaCargos(buscadorInput.value);
  });
}

/* CONEXIONES */
const API_URL = 'http://localhost:4000/graphql';

async function cargarCargosDesdeBackend() {
  const query = `
    query {
      cargos {
        id
        nombre
        descripcion
      }
    }
  `;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query }),
    });

    const json = await response.json();
    console.log("Respuesta GraphQL completa:", json);

    if (json.errors) {
      console.error("❌ Error GraphQL:", json.errors);
      return [];
    }

    return json.data.cargos;
  } catch (error) {
    console.error("❌ Error de conexión:", error);
    return [];
  }
}

async function guardarCargoEnBackend(nombre, descripcion) {
  const mutation = `
    mutation {
      createCargo(input: {
        nombre: "${nombre}",
        descripcion: "${descripcion}"
      }) {
        id
        nombre
        descripcion
      }
    }
  `;

  try {
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: mutation }),
    });

    const json = await response.json();

    if (json.errors) {
      console.error("❌ Error al guardar cargo:", json.errors);
      return null;
    }

    return json.data.createCargo;
  } catch (error) {
    console.error("❌ Error de conexión al guardar cargo:", error);
    return null;
  }
}

// Función global reutilizable
async function recargarCargos() {
  cargos = await cargarCargosDesdeBackend();
  actualizarListaCargos();
}

// Carga inicial
document.addEventListener("DOMContentLoaded", async () => {
  console.log("DOM cargado");

  const btnDescargar = document.getElementById("btnDescargarPDF");
  if (btnDescargar) {
    btnDescargar.addEventListener("click", () => {
      alert("Su PDF se descargó correctamente.");
    });
  }

  await recargarCargos();
});
