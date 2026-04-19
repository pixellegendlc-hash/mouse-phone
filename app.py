from flask import Flask, send_from_directory, request
from flask_socketio import SocketIO, emit
import os

app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'mouse-phone-secret')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

pc_clients = set()
phone_clients = set()

@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

@app.route('/health')
def health():
    return {'status': 'ok', 'pc': len(pc_clients), 'phone': len(phone_clients)}

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
        emit('registered', {'role': 'pc', 'message': 'PC connesso!'})
    elif role == 'phone':
        phone_clients.add(request.sid)
        emit('registered', {'role': 'phone', 'message': 'Telefono connesso!'})
        for s in pc_clients: emit('phone_connected', {}, to=s)

def relay(event, data):
    for s in list(pc_clients): emit(event, data, to=s)

@socketio.on('move')         
def on_move(d):        relay('move', d)
@socketio.on('click')        
def on_click(d):       relay('click', d)
@socketio.on('double_click') 
def on_dbl(d):         relay('double_click', d)
@socketio.on('drag_start')   
def on_ds(d):          relay('drag_start', d)
@socketio.on('move_drag')    
def on_md(d):          relay('move_drag', d)
@socketio.on('drag_end')     
def on_de(d):          relay('drag_end', d)
@socketio.on('scroll')       
def on_scroll(d):      relay('scroll', d)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    socketio.run(app, host='0.0.0.0', port=port, debug=False, allow_unsafe_werkzeug=True)
