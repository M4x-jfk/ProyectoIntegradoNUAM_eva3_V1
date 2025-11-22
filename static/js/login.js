document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('form');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const submitBtn = document.querySelector('button[type="submit"]');

    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            let isValid = true;
            let errorMessage = '';

            // Reset styles
            usernameInput.style.borderColor = '';
            passwordInput.style.borderColor = '';

            // Validar usuario
            if (!usernameInput.value.trim()) {
                isValid = false;
                usernameInput.style.borderColor = 'red';
                errorMessage += 'El usuario es requerido.\n';
            }

            // Validar contraseña
            if (!passwordInput.value.trim()) {
                isValid = false;
                passwordInput.style.borderColor = 'red';
                errorMessage += 'La contraseña es requerida.\n';
            }

            if (!isValid) {
                e.preventDefault();
                alert(errorMessage);
            } else {
                // Deshabilitar botón para evitar doble envío
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Ingresando...';
            }
        });
    }
});
