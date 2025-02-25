from flask import Flask, render_template, request
from flask_socketio import SocketIO, send, emit
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")  # Permitir conexiones desde cualquier origen

# Conexión a MongoDB Atlas
client = MongoClient('mongodb://GaelAlexander:3KMnALcxmrLb5Fpb@sistemadisc-shard-00-00.qngqf.mongodb.net:27017,sistemadisc-shard-00-01.qngqf.mongodb.net:27017,sistemadisc-shard-00-02.qngqf.mongodb.net:27017/?ssl=true&replicaSet=atlas-gdlunx-shard-0&authSource=admin&retryWrites=true&w=majority&appName=SistemaDisC')
db = client.chat_db
messages_collection = db.messages

connected_users = []  # Lista de usuarios conectados


@app.route('/')
def index():
    return render_template('index.html')


# Manejar la conexión de un nuevo usuario
@socketio.on('connect')
def handle_connect():
    print("Un usuario se ha conectado")


# Manejar la desconexión de un usuario
@socketio.on('disconnect')
def handle_disconnect():
    global connected_users
    sid = request.sid
    user = next((user for user in connected_users if user['sid'] == sid), None)
    if user:
        username = user['username']
        connected_users = [user for user in connected_users if user['sid'] != sid]
        emit('update_user_list', connected_users, broadcast=True)
        send({
            'username': 'Sistema',
            'message': f"{username} ha abandonado el chat"
        }, broadcast=True)
        print(f"{username} se ha desconectado")


# Manejar el evento de unirse al chat
@socketio.on('join')
def handle_join(data):
    global connected_users
    username = data['username']
    sid = request.sid
    print(f"{username} se ha unido al chat")
    connected_users.append({'username': username, 'sid': sid})
    emit('update_user_list', connected_users, broadcast=True)

    # Obtener todos los mensajes de la BD y convertir los objetos datetime a strings
    messages = list(messages_collection.find({}, {'_id': 0}))  # Excluir el campo _id
    for message in messages:
        if isinstance(message.get('timestamp'), datetime):
            message['timestamp'] = message['timestamp'].strftime('%Y-%m-%d %H:%M:%S')
    emit('load_messages', messages, to=sid)

    send({
        'username': 'Sistema',
        'message': f"{username} se ha unido al chat"
    }, broadcast=True)


# Manejar el evento de salir del chat
@socketio.on('leave')
def handle_leave(data):
    global connected_users
    username = data['username']
    sid = request.sid
    print(f"{username} ha abandonado el chat")

    # Eliminar al usuario de la lista de usuarios conectados
    connected_users = [user for user in connected_users if user['sid'] != sid]
    emit('update_user_list', connected_users, broadcast=True)

    # Notificar a todos los usuarios que alguien ha abandonado el chat
    send({
        'username': 'Sistema',
        'message': f"{username} ha abandonado el chat"
    }, broadcast=True)


# Manejar el evento de enviar mensajes
@socketio.on('message')
def handleMessage(data):
    username = data['username']
    message = data['message']
    print(f"{username}: {message}")

    # Guardar el mensaje en MongoDB
    message_data = {
        "username": username,
        "message": message,
        "timestamp": datetime.now()
    }
    messages_collection.insert_one(message_data)

    # Convertir el objeto datetime a string antes de enviar el mensaje
    data['timestamp'] = message_data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')

    # Enviar el mensaje a todos los clientes
    send(data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)