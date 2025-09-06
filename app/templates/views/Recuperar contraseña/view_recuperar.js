// recuperar_password.js

document.getElementById('recoverForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const email = document.getElementById('email').value.trim();
  const newPassword = document.getElementById('newPassword').value;
  const confirmPassword = document.getElementById('confirmPassword').value;

  // Validaciones básicas
  if (!email || !newPassword || !confirmPassword) {
    alert('Por favor completa todos los campos.');
    return;
  }

  if (newPassword !== confirmPassword) {
    alert('Las contraseñas no coinciden.');
    return;
  }

  // Simulación de éxito
  alert('Tu contraseña ha sido restablecida correctamente.');
  // Aquí podrías redirigir o enviar datos al backend
  // window.location.href = 'login.html';
});
