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
registerForm.addEventListener('submit', async function (e) {
  e.preventDefault();

  const email = document.getElementById('emailRegister')?.value;
  const pass = document.getElementById('passwordRegister')?.value;
  const confirm = document.getElementById('confirmPassword')?.value;

  if (pass && confirm && pass !== confirm) {
    alert('Las contraseñas no coinciden');
    return;
  }

  try {
    const response = await fetch("http://127.0.0.1:8000/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        email: email,
        password: pass
      })
    });

    if (!response.ok) {
      const errorData = await response.json();
      alert("Error: " + (errorData.detail || "No se pudo procesar la solicitud"));
      return;
    }

    const data = await response.json();
    console.log("Respuesta del backend:", data);

    // ✅ Guardar token en localStorage si quieres manejarlo en JS
    localStorage.setItem("access_token", data.access_token);

    // ✅ Redirigir a la vista de empresa
    window.location.href = "/empresa";

  } catch (error) {
    console.error("Error al conectar con el servidor:", error);
    alert("No se pudo conectar con el backend");
  }
});


// Al cargar la página, ajusta la altura al formulario activo
window.addEventListener('DOMContentLoaded', adjustFormHeight);
