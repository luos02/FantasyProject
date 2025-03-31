document.getElementById("loginForm").addEventListener("submit", function(event) {
    event.preventDefault(); // Evita que el formulario se envíe

    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;
    let message = document.getElementById("message");

    if (username === "Fabian" && password === "1234") {
        message.style.color = "green";
        message.textContent = "Inicio de sesión exitoso";
        setTimeout(() => {
            window.location.href = "/Index"; // Redirige a la ruta definida como Index.html en el main.py
        }, 1500);
    } else {
        message.style.color = "red";
        message.textContent = "Usuario o contraseña incorrectos";
    }
});