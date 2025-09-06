/* FUNCIONES VIEW */

// Elementos
const btnLoginTab = document.getElementById('btnLoginTab');
const btnRegisterTab = document.getElementById('btnRegisterTab');
const loginForm = document.getElementById('loginForm');
const registerForm = document.getElementById('registerForm');
const formWrapper = document.querySelector('.form-wrapper');

// Ajusta la altura del contenedor al formulario activo
function adjustFormHeight() {
  const activeForm = document.querySelector('.form-section.active');
  if (activeForm) {
    formWrapper.style.height = `${activeForm.scrollHeight}px`;
  }
}

// Función para cambiar entre formularios con transición
function switchForm(showForm, hideForm, activeBtn, inactiveBtn) {
  // Actualiza botones
  activeBtn.classList.add('active');
  inactiveBtn.classList.remove('active');

  // Transición de salida
  hideForm.classList.remove('active');
  hideForm.classList.add('exiting');

  // Espera a que termine la salida antes de mostrar el otro
  setTimeout(() => {
    hideForm.classList.remove('exiting');
    showForm.classList.add('active');
    adjustFormHeight();
  }, 250); // tiempo coincide con el transition del CSS
}

// Eventos de pestañas
btnLoginTab.addEventListener('click', () => {
  switchForm(loginForm, registerForm, btnLoginTab, btnRegisterTab);
});

btnRegisterTab.addEventListener('click', () => {
  switchForm(registerForm, loginForm, btnRegisterTab, btnLoginTab);
});

// Validación del formulario de registro
registerForm.addEventListener('submit', function (e) {
  e.preventDefault();

  const pass = document.getElementById('passwordRegister')?.value;
  const confirm = document.getElementById('confirmPassword')?.value;

  if (pass && confirm && pass !== confirm) {
    alert('Las contraseñas no coinciden');
    return;
  }

  // Aquí deberías enviar los datos al backend si es necesario
  alert('Cuenta creada correctamente (simulado)');
});

// Al cargar la página, ajusta la altura al formulario activo
window.addEventListener('DOMContentLoaded', adjustFormHeight);
