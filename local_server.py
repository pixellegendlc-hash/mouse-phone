"""
mouse-phone — Server Locale
Esegui questo sul PC per connessione via cavo USB o WiFi locale.
Latenza minima — niente internet necessario.

Installazione (una volta sola):
    py -m pip install flask flask-socketio pyautogui

Uso:
    py local_server.py

Poi sul telefono scegli "Connessione locale" e inserisci l'IP mostrato.

Per cavo USB:
    1. Collega il telefono al PC con USB
    2. Sul telefono: Impostazioni → Hotspot → Tethering USB → attiva
    3. Usa l'IP che appare qui (di solito 192.168.42.x o 192.168.137.x)
"""

import threading
import time
import socket
import os
import sys
import pyautogui
import socketio as sio_client
from flask import Flask, send_from_directory
from flask_socketio import SocketIO, emit

# ── Config ────────────────────────────────────────────────────
PORT = 5000
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0
W, H = pyautogui.size()

# ── Trova IP locale ───────────────────────────────────────────
def get_local_ips():
    ips = []
    try:
        # Tutti gli IP di tutte le interfacce
        hostname = socket.gethostname()
        for info in socket.getaddrinfo(hostname, None):
            ip = info[4][0]
            if ip.startswith(('192.168.', '10.', '172.')) and ':' not in ip:
                if ip not in ips:
                    ips.append(ip)
    except:
        pass
    # Fallback
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        if ip not in ips: ips.append(ip)
        s.close()
    except:
        pass
    return ips or ['127.0.0.1']

# ── Flask Server ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'))
app.config['SECRET_KEY'] = 'local-mouse-phone'
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

pc_clients = set()
phone_clients = set()

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@socketio.on('connect')
def on_connect():
    from flask_socketio import request
    print(f'  [+] Connesso: {request.sid}')

@socketio.on('disconnect')
def on_disconnect():
    from flask_socketio import request
    pc_clients.discard(request.sid)
    phone_clients.discard(request.sid)

@socketio.on('register')
def on_register(data):
    from flask_socketio import request
    role = data.get('role')
    if role == 'pc':
        pc_clients.add(request.sid)
        emit('registered', {'role': 'pc', 'message': 'PC locale connesso!'})
        print('  [PC] Client PC registrato')
    elif role == 'phone':
        phone_clients.add(request.sid)
        emit('registered', {'role': 'phone', 'message': 'Telefono connesso!'})
        print('  [📱] Telefono connesso!')
        for s in pc_clients:
            emit('phone_connected', {}, to=s)

def relay(event, data):
    for s in list(pc_clients):
        emit(event, data, to=s)

@socketio.on('move')        
def _(d): relay('move', d)
@socketio.on('click')       
def _(d): relay('click', d)
@socketio.on('mouse_down')  
def _(d): relay('mouse_down', d)
@socketio.on('mouse_up')    
def _(d): relay('mouse_up', d)
@socketio.on('move_drag')   
def _(d): relay('move_drag', d)
@socketio.on('drag_start')  
def _(d): relay('drag_start', d)
@socketio.on('drag_end')    
def _(d): relay('drag_end', d)
@socketio.on('scroll')      
def _(d): relay('scroll', d)

# ── Gestione mouse locale (senza client separato) ─────────────
# In modalità locale il server riceve i comandi e li esegue
# direttamente, senza passare per un secondo script.

def sc(x, y):
    return max(0, min(W-1, int(float(x)*W))), max(0, min(H-1, int(float(y)*H)))

@socketio.on('move')
def handle_move_local(data):
    try:
        x, y = sc(data['x'], data['y'])
        pyautogui.moveTo(x, y, _pause=False)
    except: pass

@socketio.on('click')
def handle_click_local(data):
    try:
        x, y = sc(data['x'], data['y'])
        btn = data.get('button','left')
        pyautogui.moveTo(x, y, _pause=False)
        time.sleep(0.03)
        pyautogui.click(x, y, button=btn, _pause=False)
        print(f'  🖱  Click {btn} ({x},{y})')
    except: pass

@socketio.on('mouse_down')
def handle_down_local(data):
    try:
        x, y = sc(data['x'], data['y'])
        pyautogui.moveTo(x, y, _pause=False)
        time.sleep(0.03)
        pyautogui.mouseDown(x, y, button='left', _pause=False)
        print(f'  🖱  MouseDown ({x},{y})')
    except: pass

@socketio.on('mouse_up')
def handle_up_local(data):
    try:
        pyautogui.mouseUp(button='left', _pause=False)
        print(f'  🖱  MouseUp')
    except: pass

@socketio.on('move_drag')
def handle_drag_move_local(data):
    try:
        x, y = sc(data['x'], data['y'])
        pyautogui.moveTo(x, y, _pause=False)
    except: pass

@socketio.on('drag_start')
def handle_drag_start_local(data):
    try:
        x, y = sc(data['x'], data['y'])
        pyautogui.moveTo(x, y, _pause=False)
        time.sleep(0.03)
        pyautogui.mouseDown(x, y, button='left', _pause=False)
        print(f'  🟠 Drag start ({x},{y})')
    except: pass

@socketio.on('drag_end')
def handle_drag_end_local(data):
    try:
        pyautogui.mouseUp(button='left', _pause=False)
        print(f'  🟠 Drag end')
    except: pass

@socketio.on('scroll')
def handle_scroll_local(data):
    try:
        delta = int(data.get('delta', 0))
        clicks = -(delta // 30)
        if clicks: pyautogui.scroll(clicks)
    except: pass

# ── Main ──────────────────────────────────────────────────────
if __name__ == '__main__':
    ips = get_local_ips()

    print()
    print('=' * 55)
    print('   🖱  MOUSE PHONE — Server Locale')
    print('=' * 55)
    print(f'\n  🖥  Schermo: {W}x{H}')
    print(f'\n  📱 Apri sul telefono uno di questi indirizzi:\n')
    for ip in ips:
        print(f'      http://{ip}:{PORT}')
    print(f'\n  ➡️  Poi scegli "Connessione locale" e inserisci')
    print(f'      l\'indirizzo sopra nel campo IP')
    print()
    print('  Per USB: Impostazioni telefono → Hotspot →')
    print('           Tethering USB → attiva')
    print()
    print('  Premi CTRL+C per fermare')
    print('=' * 55 + '\n')

    try:
        socketio.run(app, host='0.0.0.0', port=PORT,
                     debug=False, allow_unsafe_werkzeug=True)
    except KeyboardInterrupt:
        print('\n👋 Server fermato.')
