function joinChat() {
    username = document.getElementById("username").value;
    if (username.trim() === "") {
        alert("Necesitas ingresar tu nombre para entrar al chat.");
        return;
    }

    // Conectar al servidor Socket.IO
    socket = io.connect('http://127.0.0.1:5000'); //Cambiar por IP del dispositivo si quieres ser servidor del chat

    // Mostrar la interfaz del chat y ocultar la pantalla de inicio
    document.getElementById("login").style.display = "none";
    document.getElementById("chat").style.display = "block";

    // Notificar al servidor que el usuario se ha unido
    socket.emit('join', { username: username });

    // Escuchar mensajes del servidor
    socket.on('message', function(data) {
        const messageElement = document.createElement("div");
        messageElement.textContent = `${data.username}: ${data.message}`;
        document.getElementById("messages").appendChild(messageElement);
        scrollToBottom(); // Desplazar la zona de mensajes hacia abajo
    });

    // Escuchar eventos de desconexión
    socket.on('disconnect', function() {
        const messageElement = document.createElement("div");
        messageElement.textContent = `${username} se ha desconectado`;
        document.getElementById("messages").appendChild(messageElement);
        scrollToBottom(); // Desplazar la zona de mensajes hacia abajo
    });

    // Escuchar actualizaciones de la lista de usuarios
    socket.on('update_user_list', function(users) {
        const usersElement = document.getElementById("users");
        usersElement.innerHTML = '';
        users.forEach(function(user) {
            const userElement = document.createElement("div");
            userElement.textContent = user.username;
            usersElement.appendChild(userElement);
        });
    });

    // Cargar mensajes existentes
    socket.on('load_messages', function(messages) {
        const messagesElement = document.getElementById("messages");
        messagesElement.innerHTML = '';  // Limpiar mensajes anteriores
        messages.forEach(function(message) {
            const messageElement = document.createElement("div");
            if (message.timestamp) {
                messageElement.textContent = `${message.timestamp} - ${message.username}: ${message.message}`;
            } else {
                messageElement.textContent = `${message.username}: ${message.message}`;
            }
            messagesElement.appendChild(messageElement);
        });
        scrollToBottom(); // Desplazar la zona de mensajes hacia abajo
    });

    // Agregar evento para enviar mensaje al presionar "Enter"
    document.getElementById("myMessage").addEventListener("keydown", function(event) {
        if (event.key === "Enter") { // Verificar si la tecla presionada es "Enter"
            sendMessage(); // Llamar a la función para enviar el mensaje
        }
    });
}

// Función para enviar mensajes
function sendMessage() {
    const message = document.getElementById("myMessage").value;
    if (message.trim() === "") {
        return;
    }

    // Enviar el mensaje junto con el nombre del usuario
    socket.send({ username: username, message: message });

    // Limpiar el campo de entrada
    document.getElementById("myMessage").value = "";
    document.getElementById("myMessage").focus();
}

// Función para desplazar la zona de mensajes hacia abajo
function scrollToBottom() {
    const messagesElement = document.getElementById("messages");
    messagesElement.scrollTop = messagesElement.scrollHeight;
}

// Función para salir del chat
function exitChat() {
    // Notificar al servidor que el usuario ha abandonado el chat
    socket.emit('leave', { username: username });

    // Ocultar la interfaz del chat y mostrar la ventana de ingreso de nombre
    document.getElementById("chat").style.display = "none";
    document.getElementById("login").style.display = "block";

    // Limpiar el nombre de usuario
    username = "";

    // Desconectar el socket
    socket.disconnect();
}