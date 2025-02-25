from flask import Flask, render_template
from flask_socketio import SocketIO, send
from database import messages_collection
from bson.json_util import dumps
import random

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Diccionario para almacenar colores de usuarios
user_colors = {}

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(username):
    # Asignar un color único al usuario
    user_colors[username] = f"#{random.randint(0, 0xFFFFFF):06x}"
    # Notificar a todos que un usuario se ha unido
    send({'type': 'notification', 'message': f'{username} se ha unido al chat.'}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    username = data['username']
    message = data['message']
    # Guardar el mensaje en la base de datos
    messages_collection.insert_one({'username': username, 'message': message})
    # Enviar el mensaje a todos los usuarios
    send({'type': 'message', 'username': username, 'message': message, 'color': user_colors[username]}, broadcast=True)

@socketio.on('typing')
def handle_typing(username):
    # Notificar a todos que un usuario está escribiendo
    send({'type': 'typing', 'username': username}, broadcast=True)

@socketio.on('request_old_messages')
def handle_old_messages():
    try:
        # Recuperar los últimos 100 mensajes, ordenados por _id de forma descendente
        old_messages = list(messages_collection.find({}, {'_id': 0}).sort('_id', -1).limit(100))
        socketio.emit('old_messages', old_messages)
    except Exception as e:
        print("Error al recuperar mensajes antiguos:", e)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)