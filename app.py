from gevent import monkey; monkey.patch_all()

from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mouse-phone-secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

pc_clients = set()
phone_clients = set()


@app.route('/')
def index():
    return send_from_directory('static', 'index.html')


@app.route('/health')
def health():
    return {'status': 'ok', 'pc_clients': len(pc_clients), 'phone_clients': len(phone_clients)}


@socketio.on('connect')
def on_connect():
    print(f'[CONNECT] {request.sid}')


@socketio.on('disconnect')
def on_disconnect():
    pc_clients.discard(request.sid)
    phone_clients.discard(request.sid)
    print(f'[DISCONNECT] {request.sid}')


@socketio.on('register')
def on_register(data):
    role = data.get('role')
    if role == 'pc':
        pc_clients.add(request.sid)
        print(f'[PC REGISTRATO] {request.sid}')
        emit('registered', {'role': 'pc', 'message': 'PC connesso al server!'})
    elif role == 'phone':
        phone_clients.add(request.sid)
        print(f'[TELEFONO REGISTRATO] {request.sid}')
        emit('registered', {'role': 'phone', 'message': 'Telefono connesso!'})
        for pc_sid in pc_clients:
            emit('phone_connected', {}, to=pc_sid)


@socketio.on('move')
def on_move(data):
    for pc_sid in list(pc_clients):
        emit('move', data, to=pc_sid)


@socketio.on('click')
def on_click(data):
    for pc_sid in list(pc_clients):
        emit('click', data, to=pc_sid)


@socketio.on('scroll')
def on_scroll(data):
    for pc_sid in list(pc_clients):
        emit('scroll', data, to=pc_sid)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False)
