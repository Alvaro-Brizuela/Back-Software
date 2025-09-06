/* PLANTILA HEADER - SIDE BAR */

const toggleBtn = document.getElementById("toggleSidebar");
const closeBtn = document.getElementById("closeSidebar");
const sidebar = document.getElementById("sidebar");
const body = document.body;

const profileIcon = document.getElementById('profileIcon');
const dropdownMenu = document.getElementById('dropdownMenu');
const userNameDisplay = document.getElementById('userName');
const logoutBtn = document.getElementById('logoutBtn');

// Mostrar inicial y nombre
function setUserInitial(name) {
    const initial = name.trim().charAt(0).toUpperCase();
    profileIcon.textContent = initial;
    userNameDisplay.textContent = name;
}

// ACÁ VA EL NOMBRE DEL USUARIO
setUserInitial("Felipe Moscoso");

// Abrir/cerrar menú
profileIcon.addEventListener('click', () => {
    dropdownMenu.classList.toggle('show');
});

// Ocultar si clic fuera del menú
document.addEventListener('click', (event) => {
    if (
        !profileIcon.contains(event.target) &&
        !dropdownMenu.contains(event.target)
    ) {
        dropdownMenu.classList.remove('show');
    }
});

// Acción de cerrar sesión
logoutBtn.addEventListener('click', () => {
   
    // ACÁ VA LA ACCION DE CERRAR SESIÓN
    alert("Sesión cerrada");
});

// Sidebar toggle
toggleBtn.addEventListener("click", () => {
    sidebar.classList.add("show");
    toggleBtn.classList.add("hide");
});

closeBtn.addEventListener("click", () => {
    sidebar.classList.remove("show");
    toggleBtn.classList.remove("hide"); 
});

// CERRAR AL HACER CLICK AFUERA 
document.addEventListener('click', function (event) {
  const sidebar = document.getElementById('sidebar');
  const toggleBtn = document.getElementById('toggleSidebar');

  // Si el sidebar está abierto y el clic NO fue dentro del sidebar ni en el botón
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